from collections import defaultdict
import numpy as np
from sqlalchemy.orm import Session

from .repository.ActividadRepository import ActividadRepository
from .bd.conexion import getSession, getEngine
from .repository.UsuarioRepository import UsuarioRepository
from .repository.CategoriaRepository import CategoriaRepository
import tensorflow as tf
import tensorflow_recommenders as tfrs
import numpy as np

engine = getEngine()

deDatos= getSession()

with Session(getEngine()) as session:
    usuarios = []
    categorias = []
    actividades= []
    userRepo = UsuarioRepository(session)
    aRepo = ActividadRepository(session)
    CRepo = CategoriaRepository(session)
    cRepo = CategoriaRepository(session)

    datos = defaultdict(list)
    datosActividad = defaultdict(list)

    usuarios = userRepo.getUsuarios()
    for user in usuarios:
        datos[user.id].append(cRepo.getCategoriaUsuario(user.id))

    actividades = aRepo.getActividades()
    for activity in actividades:
        datosActividad[activity.id].append(CRepo.getCategoriaActividad(activity.id))

    categorias = CRepo.getCategorias()

    categorias = np.array(categorias)
    actividades = np.array(actividades)


    # Ahora puedes acceder a las dimensiones de las matrices
    num_categorias = len(categorias)#.shape[1]
    num_actividades = len(actividades)#.shape[1]
    

    print('tipo: ',str(type(categorias)))
    
    num_usuarios = len(datos)
    
    preferencias_usuarios = np.zeros((num_usuarios, num_categorias))
    claves_datos = list(datos.keys())

    for i, user_id in enumerate(claves_datos):
        for c in range(0, num_categorias):
            if c in datos[user]:
                preferencias_usuarios[i, c] = 1
            else:
                preferencias_usuarios[i, c] = 0

    # actividades_categorias = np.zeros((num_actividades, num_categorias))
    # claves_actividades = list(datosActividad.keys())

    # for i, actividad in enumerate(claves_actividades):
    #     for j in range(0, num_categorias):
    #         if j in datosActividad[actividad]:  # Ajusta esto según la estructura de tu modelo de datos
    #             actividades_categorias[i, j] = 1
    #         else:
    #             actividades_categorias[i, j] = 0

    # Crear matrices NumPy para las actividades y preferencias
    print("tamaño: actividades ", len(actividades))
    print("tamaño: preferencia ", len(preferencias_usuarios))

    # if len(actividades_categorias) > len(preferencias_usuarios):
    #     max_size = len(actividades_categorias)
    #     preferencias_usuarios = np.pad(preferencias_usuarios, ((0, max_size - len(preferencias_usuarios)), (0, 0)), 'constant')
    # else:
    #     max_size = len(preferencias_usuarios)
    #     actividades_categorias = np.pad(actividades_categorias, ((0, max_size - len(actividades_categorias)), (0, 0)), 'constant')
    if len(actividades) > len(preferencias_usuarios):
        max_size = len(actividades)
        preferencias_usuarios = np.pad(preferencias_usuarios, ((0, max_size - len(preferencias_usuarios)), (0, 0)), 'constant')
    else:
        max_size = len(preferencias_usuarios)
        actividades = np.pad(actividades, ((0, max_size - len(actividades)), (0, 0)), 'constant')
    
    preferencias_usuarios = np.array(preferencias_usuarios)
    actividades = np.array(actividades)

    users_dataset = tf.data.Dataset.from_tensor_slices(preferencias_usuarios)
    activities_dataset = tf.data.Dataset.from_tensor_slices(actividades)

    interactions_dataset = tf.data.Dataset.zip((users_dataset, activities_dataset))

    train_size = int(0.8 * len(interactions_dataset))
    train_dataset = interactions_dataset.take(train_size)
    test_dataset = interactions_dataset.skip(train_size)

    #desde aca lo nuevo
    # Define el modelo de usuario (reemplaza con tu lógica)
    user_model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(num_categorias,)),  # Input con la misma forma que las preferencias de usuarios
    tf.keras.layers.Dense(32, activation='relu'),
    # Agrega más capas si es necesario
    ])

# Define el modelo de actividad (reemplaza con tu lógica)
    activity_model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(num_categorias,)),  # Input con la misma forma que las actividades
        tf.keras.layers.Dense(32, activation='relu'),
    # Agrega más capas si es necesario
    ])

#Define tu tarea de recuperación (puede necesitar ajustes según tus preferencias)
    task = tfrs.tasks.Retrieval(metrics=tfrs.metrics.FactorizedTopK(
        activities.batch(128).map(activity_model)
    ))

# Define tu modelo de recomendación
    class MyModel(tfrs.Model):
        def __init__(self, user_model, activity_model, task):
            super().__init__()
            self.activity_model: tf.keras.Model = activity_model
            self.user_model: tf.keras.Model = user_model
            self.task: tf.keras.layers.Layer = task

    def compute_loss(self, features, training=False):
        user_embeddings = self.user_model(features["user_id"])
        activity_embeddings = self.activity_model(features["activity_id"])
        return self.task(user_embeddings, activity_embeddings)

    # Crea una instancia de tu modelo
    model = MyModel(user_model, activity_model, task)

    # Compila el modelo
    model.compile(optimizer=tf.keras.optimizers.Adagrad(0.5))

    # Entrena el modelo (reemplaza con tus datos y número de épocas)
    model.fit(preferencias_usuarios, actividades, epochs=50)

    usuario = CRepo.getCategoriaUsuario(5) 
    new = np.zeros(num_categorias, dtype=int) 
    for categoria in enumerate(usuario):
        if categoria in range(0, num_categorias):  # Asegúrate de que la categoría sea válida
            new[categoria] = 1

    recomendaciones_probabilidades = model.predict(np.array([new]))#usuario_nuevo)

    # Obtener las actividades recomendadas en palabras
    print("recom: ", recomendaciones_probabilidades)
    actividades_recomendadas = []
    for i, probabilidad in enumerate(recomendaciones_probabilidades[0]):
        print("indice", i)
        #if probabilidad > 0.7:  # Puedes ajustar este umbral según tus preferencias
        actividad = aRepo.getActividad(i+11)
        print("actividad",actividad.nombre)
        actividades_recomendadas.append(actividad.nombre)

    # Imprimir las recomendaciones de actividades
    print("Recomendaciones de actividades para el usuario:", actividades_recomendadas)

    # Guardar el modelo entrenado se guarda en h5 porque es un archivo compatible con tensorflow
    model.save("modelo.keras")

    modelo_cargado = tf.keras.models.load_model("modelo.keras")

    #aca empieza lo viejo
    #actividades_categorias = np.array(actividades_categorias)

    # Crear un modelo de recomendación con TensorFlow
    # modelo = tf.keras.Sequential([
    #     tf.keras.layers.Input(shape=(num_actividades,)), #num_categorias
    #     tf.keras.layers.Dense(16, activation='relu'),
    #     tf.keras.layers.Dense(num_actividades,activation='sigmoid') #se puede cambiar por num_categorias?
    # ])
    # #modelo.add(tf.keras.layers.Dense(4, activation='sigmoid')) 

    # # Compilar el modelo
    # modelo.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    # # Entrenar el modelo
    # #!volver a 1000
    # objetivo_entrenamiento = preferencias_usuarios.copy()
    # modelo.fit(preferencias_usuarios, objetivo_entrenamiento, epochs = 50)

    # """nuevoUsuario = np.array([[0, 0, 0, 0, 1, 0, 0, 0]])"""
    # usuario = CRepo.getCategoriaUsuario(5) 
    # new = np.zeros(num_categorias, dtype=int) 
    # for categoria in enumerate(usuario):
    #     if categoria in range(0, num_categorias):  # Asegúrate de que la categoría sea válida
    #         new[categoria] = 1

    # recomendaciones_probabilidades = modelo.predict(np.array([new]))#usuario_nuevo)

    # # Obtener las actividades recomendadas en palabras
    # print("recom: ", recomendaciones_probabilidades)
    # actividades_recomendadas = []
    # for i, probabilidad in enumerate(recomendaciones_probabilidades[0]):
    #     print("indice", i)
    #     #if probabilidad > 0.7:  # Puedes ajustar este umbral según tus preferencias
    #     actividad = aRepo.getActividad(i+11)
    #     print("actividad",actividad.nombre)
    #     actividades_recomendadas.append(actividad.nombre)

    # # Imprimir las recomendaciones de actividades
    # print("Recomendaciones de actividades para el usuario:", actividades_recomendadas)

    # # Guardar el modelo entrenado se guarda en h5 porque es un archivo compatible con tensorflow
    # modelo.save("modelo.keras")

    # modelo_cargado = tf.keras.models.load_model("modelo.keras")
