import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Usuario, Viaje, Actividad, Lugar, AgendaDiaria
from .bd.conexion import getSession
from tensorflow import Input, Embedding, LSTM, Dense
from tensorflow import Model

Session = getSession()
session = Session()

usuarios = session.query(Usuario).all()
viajes = session.query(Viaje).all()
actividades = session.query(Actividad).all()
lugares = session.query(Lugar).all()

# Ejemplo de datos de entrada (características)
# Aquí debes proporcionar los datos reales que deseas utilizar
usuario_ids = [1, 2, 1]
viaje_ids = [2, 1, 3]
actividad_ids = [3, 1, 2]
# Agrega más datos según sea necesario

# Codificar datos de entrada a números
# Supongamos que los IDs de usuarios, viajes y actividades se utilizan como características
datos_usuario_codificados = usuario_ids
datos_viaje_codificados = viaje_ids
datos_actividad_codificados = actividad_ids

# Crear una matriz de características
matriz_caracteristicas = np.array([datos_usuario_codificados, datos_viaje_codificados, datos_actividad_codificados]).T

# Datos de salida deseada (por ejemplo, la agenda)
# proporcionar datos reales de la agenda que se quieren predecir
agenda_ids = [1, 2, 3]
# Agrega más datos de salida según sea necesario

# Codificar datos de salida a números (si es necesario)
agenda_codificada = agenda_ids

# Crear un arreglo de salida deseada
salida_deseada = np.array(agenda_codificada)

longitud_secuencia = 100
num_caracteristicas = 50
embedding_dim = 32
hidden_units = 64
num_actividades = 10
longitud_salida = 10

# Definir matrices de características y salida deseada 
matriz_caracteristicas_entrenamiento = np.random.rand(1000, longitud_secuencia)  # Ejemplo de matriz de características
salida_deseada_entrenamiento = np.random.randint(0, 2, size=(1000, num_actividades))  # Ejemplo de salida deseada

# Definir tamaño de lote y número de épocas
tamaño_lote = 32
num_epocas = 10

# Define la arquitectura del modelo
def definir_modelo(longitud_secuencia, num_caracteristicas, embedding_dim, hidden_units, num_actividades):
    # Definir el Codificador
    entrada = Input(shape=(longitud_secuencia,))
    embedding = Embedding(input_dim=num_caracteristicas, output_dim=embedding_dim)(entrada)
    encoder_lstm = LSTM(units=hidden_units)(embedding)

    # Definir el Decodificador
    entrada_decoder = Input(shape=(longitud_salida,))
    embedding_decoder = Embedding(input_dim=num_actividades, output_dim=embedding_dim)(entrada_decoder)
    decoder_lstm = LSTM(units=hidden_units, return_sequences=True)(embedding_decoder)
    salida = Dense(num_actividades, activation='softmax')(decoder_lstm)

    # Definir el Modelo Completo
    modelo_completo = Model(inputs=[entrada, entrada_decoder], outputs=salida)

    # Compilar el modelo
    modelo_completo.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    
    return modelo_completo

# Llamamos a la función para definir el modelo
modelo = definir_modelo(longitud_secuencia, num_caracteristicas, embedding_dim, hidden_units, num_actividades)

# Entrenar el modelo (código relacionado con el Paso 4)
modelo.fit(matriz_caracteristicas_entrenamiento, salida_deseada_entrenamiento, epochs=num_epocas, batch_size=tamaño_lote)

# Guardar el modelo entrenado se guarda en h5 porque es un archivo compatible con tensorflow
modelo.save('modelo_entrenado.h5')

