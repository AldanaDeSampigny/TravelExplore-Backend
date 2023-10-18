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
deDatos = getSession()
with Session(getEngine()) as session:
    usuarios = []
    categorias = []
    actividades = []
    userRepo = UsuarioRepository(session)
    aRepo = ActividadRepository(session)
    CRepo = CategoriaRepository(session)
    datos = defaultdict(list)
    datosActividad = defaultdict(list)
    usuarios = userRepo.getUsuarios()
    for user in usuarios:
        datos[user.id].append(CRepo.getCategoriaUsuario(user.id))

    actividades = aRepo.getActividades()
#  EL ERROR ES COMO OBTENEMOS Y GUARDAMOS LA INFO?
    categorias_actividades = [CRepo.getCategoriaActividad(
        actividad.id) for actividad in actividades]
    max_length = max(len(seq) for seq in categorias_actividades) + 1
    categorias_actividades = [
        seq + [0] * (max_length - len(seq)) for seq in categorias_actividades]
    
    actividadesInfo = np.array(categorias_actividades, dtype=np.float32)
    
    valoraciones = [actividad.valoracion for actividad in actividades]
    print(valoraciones)

    categorias = CRepo.getCategorias()

    categorias = np.array(categorias)
    actividades = np.array(actividades)

    # Ahora puedes acceder a las dimensiones de las matrices
    num_categorias = len(categorias) + 1  # .shape[1]
    num_actividades = len(actividades)  # .shape[1]

    num_usuarios = len(datos)

    preferencias_usuarios = np.zeros((num_usuarios, (num_categorias)))
    claves_datos = list(datos.keys())

    for i, userID in enumerate(claves_datos):
        categorias_usuario = []
        for d in datos[userID]:
            for tupla in d:
                mi_tupla = tupla
                categorias_usuario.append(mi_tupla[0])  # = mi_tupla[0]

        for c in range(1, (num_categorias)):
            if c in categorias_usuario:
                preferencias_usuarios[i, c] = 1
            else:
                preferencias_usuarios[i, c] = 0

    #preferencias_usuarios = np.array(preferencias_usuarios)

    users_dataset = tf.data.Dataset.from_tensor_slices(preferencias_usuarios)
    activities_dataset = tf.data.Dataset.from_tensor_slices(actividadesInfo)
    print('tipo: ', str(type(activities_dataset)))
    
    interactions_dataset = tf.data.Dataset.zip(
        (users_dataset, activities_dataset))
    train_size = int(0.8 * len(interactions_dataset))
    train_dataset = interactions_dataset.take(train_size)
    test_dataset = interactions_dataset.skip(train_size)

    # desde aca lo nuevo
    # Define el modelo de usuario (reemplaza con tu lógica)
    user_model = tf.keras.Sequential([
        # Input con la misma forma que las preferencias de usuarios
        tf.keras.layers.Input(shape=(num_categorias,)),
        tf.keras.layers.Dense(32, activation='relu'),
        # Agrega más capas si es necesario
    ])
    # Define el modelo de actividad
    activity_model = tf.keras.Sequential([
        # Representación de la categoría
        tf.keras.layers.Input(shape=(num_categorias,)),
        # Embeddings de categoría
        tf.keras.layers.Embedding(input_dim=num_categorias, output_dim=256),
        tf.keras.layers.Flatten(),  # Aplanar los embeddings
        tf.keras.layers.Dense(256, activation='relu'),
        # Agregar más capas si es necesario
        tf.keras.layers.Dense(1)  # Capa de salida para la métrica
    ])
    # Define la entrada para el usuario y la actividad
    user_input = tf.keras.layers.Input(shape=(num_categorias,), name='input_')
    activity_input = tf.keras.layers.Input(
        shape=(num_categorias,), name='input_2')
    user_embeddings = user_model(user_input)
    activity_embeddings = activity_model(activity_input)
    model = tfrs.models.Model(user_model, activity_model, activities_dataset)
    # Define tu modelo de recomendación

    class MyModel(tfrs.Model):
        def __init__(self, user_model, activity_model, task):
            super().__init__()
            self.activity_model: tf.keras.Model = activity_model
            self.user_model: tf.keras.Model = user_model
            self.task: tf.keras.layers.Layer = task

        def compute_loss(self, features, training=False):
            print(features)
            print(features[0]['input_1'])
            print(str(type(features[1])))
            user_embeddings = self.user_model(features[0]['input_1'])
            activity_embeddings = self.activity_model(features[0]['input_2'])
            return self.task(user_embeddings, activity_embeddings)

        # Crea una instancia de tu modelo
    model = MyModel(user_model, activity_model, activities_dataset)

    # Compila el modelo
    model.compile(optimizer=tf.keras.optimizers.Adagrad(
        0.5), loss='mean_squared_error')

    preferencias_usuarios_tensor = tf.convert_to_tensor(
        preferencias_usuarios, dtype=tf.float32)
    actividadesInfo_tensor = tf.convert_to_tensor(
        actividadesInfo, dtype=tf.float32)

    print("tam p: ", len(preferencias_usuarios_tensor))
    print("tam a: ", len(actividadesInfo_tensor))

    print("actividad")
    print(actividadesInfo_tensor)

    train_data = {
        'input_1': preferencias_usuarios_tensor,
        'input_2': actividadesInfo_tensor,
    }

    # Continuar con el entrenamiento del modelo
    model.fit(train_data, np.array(valoraciones, dtype=np.float32), epochs=50)

    usuario = CRepo.getCategoriaUsuario(5)
    new = np.zeros(num_categorias, dtype=int)
    for categoria in enumerate(usuario):
        # Asegúrate de que la categoría sea válida
        if categoria in range(0, num_categorias):
            new[categoria] = 1

    recomendaciones_probabilidades = model.predict(
        np.array([new]))  # usuario_nuevo)

    # Obtener las actividades recomendadas en palabras
    print("recom: ", recomendaciones_probabilidades)
    actividades_recomendadas = []
    for i, probabilidad in enumerate(recomendaciones_probabilidades[0]):
        print("indice", i)
        # if probabilidad > 0.7:  # Puedes ajustar este umbral según tus preferencias
        actividad = aRepo.getActividad(i+11)
        print("actividad", actividad.nombre)
        actividades_recomendadas.append(actividad.nombre)
    # Imprimir las recomendaciones de actividades
    print("Recomendaciones de actividades para el usuario:",
          actividades_recomendadas)
    # Guardar el modelo entrenado se guarda en h5 porque es un archivo compatible con tensorflow
    model.save("modelo.keras")
    modelo_cargado = tf.keras.models.load_model("modelo.keras")
    