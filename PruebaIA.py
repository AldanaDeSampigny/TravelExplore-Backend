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


# engine = getEngine()
# deDatos = getSession()

class PruebaIA:
    def __init__(self, db_session):
        self.db_session = db_session

    def cargadoDeIA(self, usuarioID):
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
            
            interactions_dataset = tf.data.Dataset.zip(
                (activities_dataset))
            train_size = int(0.8 * len(interactions_dataset))

            train_dataset = interactions_dataset.take(train_size)
            test_dataset = interactions_dataset.skip(train_size)

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

                def call(self, inputs, training=False):
                    user_embeddings = self.user_model(inputs['input_1'])
                    activity_embeddings = self.activity_model(inputs['input_2'])
                    return self.task(user_embeddings, activity_embeddings)

            model = MyModel(user_model, activity_model, task)

            optimizer = tf.keras.optimizers.Adagrad(0.1)
            loss_fn = tf.keras.losses.MeanSquaredError()  # tfrs.pointwise()

            # Compila el modelo con el optimizador y la función de pérdida
            model.compile(optimizer)#, loss=loss_fn)
            # Cargar los pesos en el modelo

            dummy_input = {
                'input_1': tf.zeros((1, num_categorias), dtype=tf.float32),
                'input_2': tf.zeros((1, num_categorias), dtype=tf.float32)
            }
            _ = model(dummy_input)

            model.load_weights('modeloConH5.h5')#'modeloConH5.h5')

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
            #new_tensor = tf.expand_dims(new_tensor, axis=0)
            actividadesInfo_tensor = tf.convert_to_tensor(actividadesInfo, dtype=tf.float32)

            index = tfrs.layers.factorized_top_k.BruteForce(model.user_model)
            index.index_from_dataset(tf.data.Dataset.zip((activities_dataset.batch(100), activities_dataset.batch(100).map(model.activity_model)))) 

            _, top_recommendations = index(np.array([new_tensor], dtype=np.int32))
            #solo el top 3 FUNCIONAAA
            #top_3_recommendations = top_recommendations[0, :5]
            top_3_recommendations = top_recommendations[0, :5].numpy()
            print(f"Las mejores recomendaciones para el usuario: {top_3_recommendations}") 
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

        # SELECT id_actividad
        # FROM actividades_categorias
        # WHERE id_categoria = any(array[1, 10])
        # GROUP BY id_actividad
        # HAVING count(id_actividad) = 2;


