from collections import defaultdict
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .repository.ActividadRepository import ActividadRepository
from .models import Usuario, Viaje, Actividad, Lugar, AgendaDiaria
from .bd.conexion import getSession, getEngine
from .repository.UsuarioRepository import UsuarioRepository
from .repository.CategoriaRepository import CategoriaRepository
import tensorflow as tf
import numpy as np
import tensorflow_recommenders as tfrs
from typing import Dict, Text
from sqlalchemy.orm import sessionmaker

engine = getEngine()

deDatos= getSession()

#class Entrenamiento:
with Session(getEngine()) as session:
    usuarios = []
    categorias = []
    actividades= []
    userRepo = UsuarioRepository(session)
    aRepo = ActividadRepository(session)
    CRepo = CategoriaRepository(session)

    datos = defaultdict(list)
    cRepo = CategoriaRepository(session)
    usuarios = userRepo.getUsuarios()

    for user in usuarios:
        datos[user.id].append(cRepo.getCategoriaUsuario(user.id))

    actividades = aRepo.getActividades()

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

    # Crear matrices NumPy para las actividades y preferencias
    preferencias_usuarios = np.array(preferencias_usuarios)

    # Crear un modelo de recomendación con TensorFlow
    modelo = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(num_categorias,)), #num_categorias
        tf.keras.layers.Dense(16, activation='relu'),
        tf.keras.layers.Dense(num_actividades, activation='sigmoid') #num_actividades
    ])

    # Compilar el modelo
    modelo.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    # Entrenar el modelo
    modelo.fit(preferencias_usuarios, actividades, epochs = 1000)
    #modelo.fit(usuarios_map, actividades, epochs=1000)

    usuario_nuevo = np.array(UsuarioRepository(session)).getUsuarioCategoria(5)#[0, 0, 1, 0, 1])
    recomendaciones_probabilidades = modelo.predict(np.array([usuario_nuevo]))

    # Obtener las actividades recomendadas en palabras
    actividades_recomendadas = []
    for i, probabilidad in enumerate(recomendaciones_probabilidades[0]):
        if probabilidad > 0.5:  # Puedes ajustar este umbral según tus preferencias
            actividad = aRepo.getActividad(i)
            actividades_recomendadas.append(actividad)

    # Imprimir las recomendaciones de actividades
    print("Recomendaciones de actividades para el usuario:", actividades_recomendadas)

    # Guardar el modelo entrenado se guarda en h5 porque es un archivo compatible con tensorflow
    modelo.save('modelo_entrenado.h5')


# # Ratings data.
# ratings = tfds.load('movielens/100k-ratings', split="train")
# # Features of all the available movies.
# movies = tfds.load('movielens/100k-movies', split="train")

# # Select the basic features.
# ratings = ratings.map(lambda x: {
#     "movie_title": x["movie_title"],
#     "user_id": x["user_id"]
# })
# movies = movies.map(lambda x: x["movie_title"])
# user_ids_vocabulary = tf.keras.layers.StringLookup(mask_token=None)
# user_ids_vocabulary.adapt(ratings.map(lambda x: x["user_id"]))

# movie_titles_vocabulary = tf.keras.layers.StringLookup(mask_token=None)
# movie_titles_vocabulary.adapt(movies)
""" class MovieLensModel(tfrs.Model):
  # We derive from a custom base class to help reduce boilerplate. Under the hood,
  # these are still plain Keras Models.

  def __init__(
      self,
      user_model: tf.keras.Model,
      movie_model: tf.keras.Model,
      task: tfrs.tasks.Retrieval):
    super().__init__()

    # Set up user and movie representations.
    self.user_model = user_model
    self.movie_model = movie_model

    # Set up a retrieval task.
    self.task = task

  def compute_loss(self, features: Dict[Text, tf.Tensor], training=False) -> tf.Tensor:
    # Define how the loss is computed.

    user_embeddings = self.user_model(features["user_id"])
    movie_embeddings = self.movie_model(features["movie_title"])

    return self.task(user_embeddings, movie_embeddings) 

    
    # Define user and movie models.
user_model = tf.keras.Sequential([
    user_ids_vocabulary,
    tf.keras.layers.Embedding(user_ids_vocabulary.vocab_size(), 64)
])
movie_model = tf.keras.Sequential([
    movie_titles_vocabulary,
    tf.keras.layers.Embedding(movie_titles_vocabulary.vocab_size(), 64)
])

# Define your objectives.
task = tfrs.tasks.Retrieval(metrics=tfrs.metrics.FactorizedTopK(
    movies.batch(128).map(movie_model)
  )
)



usuario = []
categoria = []
usuario.append(UsuarioRepository(getEngine()).getUsuarios())

datos = []
for u in usuario:
    datos.append(u.id, CategoriaRepository(getEngine()).getCategoriaUsuario(u.id))
    #categoria = CategoriaRepository.getCategoriaUsuario(u.id)"""



    # Crear mapas de palabras a números
    # categorias_map = {
    #     "Comida Italiana": 0,
    #     "Deportes Acuáticos": 1,
    #     "Senderismo": 2,
    #     "Museos de Arte": 3,
    #     "Fotografía de Naturaleza": 4
    # }

    # actividades_map = {
    #     0: "Almuerzo en Trattoria Italiana",
    #     1: "Paseo en Bote por el Lago",
    #     2: "Escalada en Montaña"
    #     # Agrega más actividades según sea necesario
    # }

    # usuarios_map = { #usuarios relacionados con categorias
    #     "Usuario 1": [0, 1, 0, 0, 1],
    #     "Usuario 2": [0, 0, 0, 1, 0],
    #     "Usuario 3": [0, 0, 0, 0, 0]
    #     # Agrega más usuarios según sea necesario
    # }

    # # Reemplazar datos numéricos por palabras
    # categorias = np.array([
    #     [1, 0, 0, 0, 0],  # Categoría 1: Comida Italiana
    #     [0, 1, 1, 0, 0],  # Categoría 2: Deportes Acuáticos y Senderismo
    #     [0, 0, 0, 1, 1]   # Categoría 3: Museos de Arte y Fotografía de Naturaleza
    # ])

    # actividades = np.array([
    #     [1, 0, 0],  # Almuerzo en Trattoria Italiana
    #     [0, 1, 0],  # Paseo en Bote por el Lago
    #     [0, 0, 1]   # Escalada en Montaña
    # ])