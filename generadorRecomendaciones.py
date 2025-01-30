from collections import defaultdict
import tensorflow as tf
import tensorflow_recommenders as tfrs

from .repository.ActividadRepository import ActividadRepository
from .repository.UsuarioRepository import UsuarioRepository
from .repository.CategoriaRepository import CategoriaRepository

from .bd.conexion import getEngine
from sqlalchemy.orm import Session
import numpy as np

class GeneradorRecomendaciones:
    def __init__(self, modelo_recomendacion):
        self.modelo_recomendacion = modelo_recomendacion

        with Session(getEngine()) as session:
            self.categoriaRepository = CategoriaRepository(session)
            self.actividadesRepository = ActividadRepository(session)
            categorias_actividades = defaultdict(list)

            categorias = self.categoriaRepository.getCategorias()
            categorias = np.array(categorias)
            actividades = self.actividadesRepository.getActividades()
            actividades = np.array(actividades)

            self.num_categorias = len(categorias) + 1 
            self.num_actividades = len(actividades)  

            #!Metodo nuevo para separar todo esta parte de codigo 
            #!def armadoDeInfoActividades(actividades)
            
            for acti in actividades:
                categorias_actividades[acti.id].append(self.categoriaRepository.getCategoriaActividad(acti.id))

            actividadesInfo = np.zeros((self.num_actividades, (self.num_categorias)))
            actividadDatos = list(categorias_actividades.keys())

            for i, actividadID in enumerate(actividadDatos):
                actividades_categorias = [] 
                for categoria in categorias_actividades[actividadID]:
                    actividades_categorias.append(categoria)
                
                for c in range(0, self.num_categorias):
                    inner_list = actividades_categorias[0] if actividades_categorias else [] 
                    if c in inner_list:
                        actividadesInfo[i, c] = 1
                    else:
                        actividadesInfo[i, c] = 0

            self.activities_dataset = tf.data.Dataset.from_tensor_slices(actividadesInfo)

    def generar_recomendaciones(self, usuarioID):
        categoriasDelUsuario = self.categoriaRepository.getCategoriaUsuario(usuarioID)
        new = np.zeros(self.num_categorias, dtype=int)
        for i in range(1, self.num_categorias):
            for categoria in enumerate(categoriasDelUsuario): 
                if i == categoria[1][0]:
                    new[i] = 1
                else:
                    new[i] = 0

                new_tensor = tf.convert_to_tensor(new, dtype=tf.float32)

        index = tfrs.layers.factorized_top_k.BruteForce(self.modelo_recomendacion.user_model)
        index.index_from_dataset(tf.data.Dataset.zip(
            (self.activities_dataset.batch(100), self.activities_dataset.batch(100).map(self.modelo_recomendacion.activity_model)))) 

        _, top_recommendations = index(np.array([new_tensor], dtype=np.int32))
        
        top_3_recommendations = top_recommendations[0, :5].numpy()
    
        actividadReco = []  

        for filaRecomendacion in top_3_recommendations:
            indicesCategoria = []  

            for columnaRecomendacion in range(0, len(filaRecomendacion)):
                if filaRecomendacion[columnaRecomendacion] == 1.0:
                    indicesCategoria.append(columnaRecomendacion)

            actividades = self.actividadesRepository.getActividadCategorias(indicesCategoria)

            actividadReco.extend(actividades)  

        return actividadReco