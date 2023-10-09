import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Usuario, Viaje, Actividad, Lugar, AgendaDiaria
from .bd.conexion import getSession, getEngine
from .repository.UsuarioRepository import UsuarioRepository
import numpy as np
import tensorflow_recommenders as tfrs
from typing import Dict, Text

import numpy as np
import tensorflow as tf
from typing import Dict, Text


# Crear mapas de palabras a números
categorias_map = {
    "Comida Italiana": 0,
    "Deportes Acuáticos": 1,
    "Senderismo": 2,
    "Museos de Arte": 3,
    "Fotografía de Naturaleza": 4
}

actividades_map = {
    0: "Almuerzo en Trattoria Italiana",
    1: "Paseo en Bote por el Lago",
    2: "Escalada en Montaña"
    # Agrega más actividades según sea necesario
}

usuarios_map = { #tiene las actividades que le gusta
    "Usuario 1": [0, 1, 0, 0, 1],
    "Usuario 2": [0, 0, 0, 1, 0],
    "Usuario 3": [0, 0, 0, 0, 0]
    # Agrega más usuarios según sea necesario
}

usuarios = np.array([[0, 1, 0, 0, 1],  # Usuario 1: Le gusta la comida italiana, museos de arte y fotografía de naturaleza
                     [0, 0, 0, 1, 0],  # Usuario 2: Le gusta el senderismo
                     [0, 0, 0, 0, 0],  # Usuario 3: No tiene preferencias
                     # Agrega más usuarios según sea necesario
                     ])

# Reemplazar datos numéricos por palabras
categorias = np.array([
    [1, 0, 0, 0, 0],  # Categoría 1: Comida Italiana
    [0, 1, 1, 0, 0],  # Categoría 2: Deportes Acuáticos y Senderismo
    [0, 0, 0, 1, 1]   # Categoría 3: Museos de Arte y Fotografía de Naturaleza
])

actividades = np.array([
    [1, 0, 0],  # Almuerzo en Trattoria Italiana
    [0, 1, 0],  # Paseo en Bote por el Lago
    [0, 0, 1]   # Escalada en Montaña
])

# Crear un modelo de recomendación con TensorFlow
modelo = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(categorias.shape[1],)),
    tf.keras.layers.Dense(16, activation='relu'),
    tf.keras.layers.Dense(actividades.shape[1], activation='sigmoid')
])

# Compilar el modelo
modelo.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Entrenar el modelo
modelo.fit(usuarios, actividades, epochs=50)
#"Usuario 3": [0, 0, 0, 0, 0]
# Realizar predicciones para un usuario
usuario_nuevo = np.array([0, 0, 1, 1, 0])#usuarios_map["Usuario 1"])
recomendaciones_probabilidades = modelo.predict(np.array([usuario_nuevo]))

# Obtener las actividades recomendadas en palabras
actividades_recomendadas = []
for i, probabilidad in enumerate(recomendaciones_probabilidades[0]):
    if probabilidad > 0.5:  # Puedes ajustar este umbral según tus preferencias
        actividades_recomendadas.append(actividades_map[i])

# Imprimir las recomendaciones de actividades
print("Recomendaciones de actividades para el usuario:", actividades_recomendadas)

# Guardar el modelo entrenado se guarda en h5 porque es un archivo compatible con tensorflow
#modelo.save('modelo_entrenado.h5')