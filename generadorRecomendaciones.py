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
    def __init__(self, modelo_recomendacion, db_session):
        self.modelo_recomendacion = modelo_recomendacion
        self.db_session = db_session

    def generar_recomendaciones(self, usuarioID):
        if not self.modelo_recomendacion:
            raise ValueError("El modelo no ha sido cargado. Por favor, carga el modelo primero.")
        
        with Session(getEngine()) as session:
            aRepo = ActividadRepository(session)
            CRepo = CategoriaRepository(session)
            categorias_actividades = defaultdict(list)

            categorias = CRepo.getCategorias()
            categorias = np.array(categorias)
            actividades = aRepo.getActividades()
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
            # Continuar con las predicciones utilizando el modelo cargado
            categoriasDelUsuario = CRepo.getCategoriaUsuario(usuarioID)
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

            index = tfrs.layers.factorized_top_k.BruteForce(self.modelo_recomendacion.user_model)
            index.index_from_dataset(tf.data.Dataset.zip(
                (activities_dataset.batch(100), activities_dataset.batch(100).map(self.modelo_recomendacion.activity_model)))) 

            _, top_recommendations = index(np.array([new_tensor], dtype=np.int32))
            
            top_3_recommendations = top_recommendations[0, :5].numpy()
            #print(f"Las mejores recomendaciones para el usuario: {top_3_recommendations}") 
            actividadReco = []  # Lista para almacenar las actividades relacionadas con las categorías

            for filaRecomendacion in top_3_recommendations:
                indicesCate = []  # Lista para almacenar los índices de las categorías relevantes para cada fila

                for columnaRecomendacion in range(0, len(filaRecomendacion)):
                    if filaRecomendacion[columnaRecomendacion] == 1.0:
                        indicesCate.append(columnaRecomendacion)

                # Busca actividades a partir de las categorías
                actividades = aRepo.getActividadCategorias(indicesCate) # Ejecuta la consulta y obtén todos los resultados

                actividadReco.extend(actividades)  # Agrega las actividades relacionadas a la lista actividadRec

            #Ahora actividadReco contiene todas las atividades relacionadas con las categorías

        return actividadReco