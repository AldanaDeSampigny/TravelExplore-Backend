import tensorflow_recommenders as tfrs
from tensorflow import keras
import numpy as np
from collections import defaultdict
import tensorflow as tf
from .repository.ActividadRepository import ActividadRepository
from .repository.UsuarioRepository import UsuarioRepository
from .repository.CategoriaRepository import CategoriaRepository
from .bd.conexion import getSession, getEngine
from sqlalchemy.orm import Session


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
    categorias_actividades = defaultdict(list)
    datosActividad = defaultdict(list)
    
    usuarios = userRepo.getUsuarios()
    for user in usuarios:
        datos[user.id].append(CRepo.getCategoriaUsuario(user.id))
    
    actividades = aRepo.getActividades()

    categorias = CRepo.getCategorias()

    categorias = np.array(categorias)
    actividades = np.array(actividades)

    # Ahora puedes acceder a las dimensiones de las matrices
    num_categorias = len(categorias) + 1  
    num_actividades = len(actividades)  

    num_usuarios = len(datos)
    
    for acti in actividades:
        categorias_actividades[acti.id].append(CRepo.getCategoriaActividad(acti.id))


    actividadesInfo = np.zeros((num_actividades, (num_categorias)))
    actividadDatos = list(categorias_actividades.keys())

    for i, actividadID in enumerate(actividadDatos):
        actividades_categorias = [] 
        for categoria in categorias_actividades[actividadID]:
            actividades_categorias.append(categoria)
        
        for c in range(0, num_categorias):
            inner_list = actividades_categorias[0] if actividades_categorias else [] 
            if c in inner_list:
                actividadesInfo[i, c] = 1
            else:
                actividadesInfo[i, c] = 0

    activities_dataset = tf.data.Dataset.from_tensor_slices(actividadesInfo)
    
    # Definir la misma arquitectura del modelo
    user_model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(num_categorias,)),
        tf.keras.layers.Dense(32, activation='relu'),
    ])

    activity_model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(num_categorias,)),
        tf.keras.layers.Embedding(input_dim=num_categorias, output_dim=256),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(256, activation='relu'),
        tf.keras.layers.Dense(32),
    ])

    # Definir la entrada para el usuario y la actividad
    user_input = tf.keras.layers.Input(shape=(num_categorias,), name='input_1')
    activity_input = tf.keras.layers.Input(shape=(num_categorias,), name='input_2')

    user_embeddings = user_model(user_input)
    activity_embeddings = activity_model(activity_input)

    # Definir el mismo modelo de tfrs.Model
    task = tfrs.tasks.Retrieval(metrics=tfrs.metrics.FactorizedTopK(
        activities_dataset.batch(128).map(activity_model)
    ))

    class MyModel(tfrs.Model):
        def __init__(self, user_model, activity_model, task):
            super().__init__()
            self.activity_model = activity_model
            self.user_model = user_model
            self.task = task

        def compute_loss(self, features, training=False):
            user_embeddings = self.user_model(features['input_1'])
            activity_embeddings = self.activity_model(features['input_2'])
            return self.task(user_embeddings, activity_embeddings)
    
    # def get_config(self):
    #     #Devuelve un diccionario con la configuración del modelo
    #     #Puedes personalizar esto según tu modelo
    #     config = super(MyModel, self).get_config()
    #     #Agrega cualquier configuración específica de tu modelo al diccionario
    #     return config 

    model = MyModel(user_model, activity_model, task)

    model.build(((None, num_categorias), (None, num_categorias)))
    # Cargar los pesos en el modelo
    model.load_weights('pesos_modeloConH5.h5')

    # Continuar con las predicciones utilizando el modelo cargado
    categoriasDelUsuario = CRepo.getCategoriaUsuario(22)
    new = np.zeros(num_categorias, dtype=int)
    usuarioCategoria = []
    for i in range(1, num_categorias):
        for categoria in enumerate(categoriasDelUsuario):
            if i == categoria[1][0]:
                new[i] = 1
            else:
                new[i] = 0

    # Crear el tensor de entrada con las preferencias del usuario
    new_tensor = tf.convert_to_tensor(new, dtype=tf.float32)
    actividadesInfo_tensor = tf.convert_to_tensor(actividadesInfo, dtype=tf.float32)

    # Obtener recomendaciones para el usuario
    _, recommended_indices = model({'input_1': new_tensor, 'input_2': actividadesInfo_tensor})
    print(f"Recomendaciones para el usuario: {recommended_indices[0, 6:9]}")


# import tensorflow_recommenders as tfrs
# from tensorflow import keras
# import numpy as np
# from collections import defaultdict
# from tensorflow.keras.models import load_model
# from .bd.conexion import getSession, getEngine
# from sqlalchemy.orm import Session
# import tensorflow as tf

# from .repository.ActividadRepository import ActividadRepository
# from .repository.UsuarioRepository import UsuarioRepository
# from .repository.CategoriaRepository import CategoriaRepository


# ## It can be used to reconstruct the model identically.
# #reconstructed_model = keras.models.load_model("my_model.keras")
# #model = tf.saved_model.load('modeloConH5.h5')#tf.load_model('modelo.keras')
# #loaded_model = keras.models.load_model('modeloConH5.h5')
# model = keras.models.load_weights('modeloConH5.h5')
# #model = load_model(arguments['model'])

# engine = getEngine()
# deDatos = getSession()
# with Session(getEngine()) as session:
#     categorias_actividades = defaultdict(list)
#     userRepo = UsuarioRepository(session)
#     aRepo = ActividadRepository(session)
#     CRepo = CategoriaRepository(session)

#     actividades = aRepo.getActividades()

#     categorias = CRepo.getCategorias()

#     categorias = np.array(categorias)
#     actividades = np.array(actividades)

#     num_categorias = len(categorias) + 1  
#     num_actividades = len(actividades)  

#     for acti in actividades:
#         categorias_actividades[acti.id].append(CRepo.getCategoriaActividad(acti.id))


#     actividadesInfo = np.zeros((num_actividades, (num_categorias)))
#     actividadDatos = list(categorias_actividades.keys())

#     for i, actividadID in enumerate(actividadDatos):
#         actividades_categorias = [] 
#         for categoria in categorias_actividades[actividadID]:
#             actividades_categorias.append(categoria)
        
#         for c in range(0, num_categorias):
#             inner_list = actividades_categorias[0] if actividades_categorias else [] 
#             if c in inner_list:
#                 actividadesInfo[i, c] = 1
#             else:
#                 actividadesInfo[i, c] = 0

#     activities_dataset = tf.data.Dataset.from_tensor_slices(actividadesInfo)

#     categoriasDelUsuario = CRepo.getCategoriaUsuario(22)
#     new = np.zeros(num_categorias, dtype=int)
#     usuarioCategoria= []
#     for i in range(1, num_categorias):
#         for categoria in enumerate(categoriasDelUsuario):
#             if i == categoria[1][0]:
#                 new[i] = 1
#             else:
#                 new[i] = 0

#     # Crear el tensor de entrada con las preferencias del usuario
#     new_tensor = tf.convert_to_tensor(new, dtype=tf.float32)

#     # Crear el índice para hacer recomendaciones
#     index = tfrs.layers.factorized_top_k.BruteForce(model.user_model)


#     # Indexar desde el dataset de actividades
#     index.index_from_dataset(
#         tf.data.Dataset.zip((activities_dataset.batch(100), activities_dataset.batch(100).map(model.activity_model)))
#     )

#     # Obtener recomendaciones para el usuario
#     _, recommended_indices = model(new)#index(np.array([new_tensor], dtype=np.int32))
#     print(f"Recomendaciones para el usuario: {recommended_indices[0, 6:9]}")
#     #new_model = keras.models.load_model('path_to_my_model.h5')s