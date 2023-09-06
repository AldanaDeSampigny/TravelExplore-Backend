from flask import Flask

from .models.meGusta import MeGusta
from .models.usuario import usuario
from .models.destino import destino
from .models.viaje import Viaje
from .models.agenda import Agenda
from .bd.conexion import getSession, getEngine

app = Flask(__name__)

# Define la aplicación Flask antes de crear las tablas
baseDeDatos = getSession()
nuevo_usuario = usuario()
nuevo_destino = destino()
nuevo_viaje = Viaje()
nueva_agenda = Agenda()
nuevo_meGusta = MeGusta()

@app.route('/', methods=['GET'])
def clean_publications():
    return "Hola mundo!"
