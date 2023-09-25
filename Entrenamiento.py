import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Usuario, Viaje, Actividad, Lugar, AgendaDiaria
from .bd.conexion import getSession

import tensorflow as tf
import numpy as np

# Datos de usuarios y categorías
usuarios = np.array([[0, 1, 0, 0, 1],  # Usuario 1: Le gusta la comida italiana, museos de arte y fotografía de naturaleza
                     [0, 0, 0, 1, 0],  # Usuario 2: Le gusta el senderismo
                     [0, 0, 0, 0, 0],  # Usuario 3: No tiene preferencias
                     # Agrega más usuarios según sea necesario
                     ])

categorias = np.array([[0, 0, 1, 0, 0],  # Categoría 1: Comida Italiana
                       [0, 1, 0, 1, 0],  # Categoría 2: Deportes Acuáticos y Senderismo
                       [1, 0, 0, 1, 1],  # Categoría 3: Museos de Arte y Fotografía de Naturaleza
                       # Agrega más categorías según sea necesario
                       ])

# Datos de actividades (las utilizaremos como etiquetas)
actividades = np.array([[16, 0, 0, 1],  # Almuerzo en Trattoria Italiana
                        [17, 0, 1, 0],  # Paseo en Bote por el Lago
                        [19, 1, 0, 1],  # Escalada en Montaña
                        # Agrega más actividades según sea necesario
                        ])

# Crear un modelo de recomendación con TensorFlow
modelo = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(categorias.shape[1],)),
    tf.keras.layers.Dense(16, activation='relu'),
    tf.keras.layers.Dense(actividades.shape[1], activation='sigmoid')  # Utilizamos sigmoid para obtener probabilidades
])

# Compilar el modelo
modelo.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Entrenar el modelo
modelo.fit(categorias, actividades, epochs=1000)

# Realizar predicciones para un usuario
usuario_nuevo = np.array([0, 1, 0, 0, 1])  # Usuario 1
recomendaciones_probabilidades = modelo.predict(np.array([usuario_nuevo]))

# Imprimir las probabilidades de realizar actividades
print("Probabilidades de realizar actividades para el usuario:")

# Guardar el modelo entrenado se guarda en h5 porque es un archivo compatible con tensorflow
modelo.save('modelo_entrenado.h5')

