import tensorflow_recommenders as tfrs
import numpy as np
from collections import defaultdict
from tensorflow.keras.models import load_model
from .bd.conexion import getSession, getEngine
from sqlalchemy.orm import Session
import tensorflow as tf

from .repository.ActividadRepository import ActividadRepository
from .repository.UsuarioRepository import UsuarioRepository
from .repository.CategoriaRepository import CategoriaRepository

model = tf.keras.models.load_model('modelo.keras')#tf.load_model('modelo.keras')

engine = getEngine()
deDatos = getSession()
with Session(getEngine()) as session:
    categorias_actividades = defaultdict(list)
    userRepo = UsuarioRepository(session)
    aRepo = ActividadRepository(session)
    CRepo = CategoriaRepository(session)

    actividades = aRepo.getActividades()

    categorias = CRepo.getCategorias()

    categorias = np.array(categorias)
    actividades = np.array(actividades)

    num_categorias = len(categorias) + 1  
    num_actividades = len(actividades)  

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

    categoriasDelUsuario = CRepo.getCategoriaUsuario(22)
    new = np.zeros(num_categorias, dtype=int)
    usuarioCategoria= []
    for i in range(1, num_categorias):
        for categoria in enumerate(categoriasDelUsuario):
            if i == categoria[1][0]:
                new[i] = 1
            else:
                new[i] = 0

    # Crear el tensor de entrada con las preferencias del usuario
    new_tensor = tf.convert_to_tensor(new, dtype=tf.float32)

    # Crear el índice para hacer recomendaciones
    index = tfrs.layers.factorized_top_k.BruteForce(model.user_model)


    """ users_dataset = tf.data.Dataset.from_tensor_slices(preferencias_usuarios)
    activities_dataset = tf.data.Dataset.from_tensor_slices(actividadesInfo) """
    # Indexar desde el dataset de actividades
    index.index_from_dataset(
        tf.data.Dataset.zip((activities_dataset.batch(100), activities_dataset.batch(100).map(model.activity_model)))
    )

    # Obtener recomendaciones para el usuario
    _, recommended_indices = model(new)#index(np.array([new_tensor], dtype=np.int32))
    print(f"Recomendaciones para el usuario: {recommended_indices[0, 6:9]}")
    #new_model = keras.models.load_model('path_to_my_model.h5')s