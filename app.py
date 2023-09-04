from flask import Flask
from .bd.conexion import getSession,getEngine
from .models.SitioTuristico import SitioTuristico # Reemplaza 'mi_modelo' y 'MiTabla' con tu propio modelo y tabla
#import requests

app = Flask(__name__)

baseDeDatos = getSession()

nuevo_registro = SitioTuristico()


# url = 'https://developers.google.com/maps/documentation/places/web-service?hl=es-419'  # Reemplaza esto con la URL de la API que deseas usar
# response = requests.get(url)

# # Verifica si la solicitud fue exitosa (código de estado 200)
# if response.status_code == 200:
#     data = response.json()  # Convierte la respuesta JSON en un diccionario de Python
#     print(data)
# else:
#     print('Error en la solicitud. Código de estado:', response.status_code)



@app.route('/', methods=['GET'])
def clean_publications():
    return "Hola mundo!"


#schedule_automatic_trains()

