from flask import Flask, render_template

import json

from .utils.AlchemyEncoder import AlchemyEncoder
from .models.MeGustas import MeGustas

from .service.AgendaService import AgendaService
from .service.GustaService import GustaService

from .models.Usuarios import Usuarios
from .models.Destinos import Destinos
from .models.Viajes import Viajes
from .models.Actividad import Actividad
from .models.Agendas import Agendas
from .models.DiaViaje import DiaViaje
from .bd.conexion import getSession, getEngine, Base

app = Flask(__name__)
DeDatos = getSession()
engine = getEngine()
Base.metadata.create_all(engine)

nuevo_usuario = Usuarios()
nuevo_destino = Destinos()
nuevo_viaje = Viajes()
nuevo_dia_viaje = DiaViaje()
nueva_actividad = Actividad()
nueva_agenda = Agendas()
nuevo_meGusta = MeGustas()

@app.route('/', methods=['GET'])
def clean_publications():
    return "Hola mundo!"

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/gustos', methods=['GET'])
def show_activity():
    gustos = GustaService().get_activities()  # Llama al método get_activities para obtener los datos
    #print (gustos)
    return render_template('gustos_detail.html', activities=gustos)

@app.route('/generar_agenda/<int:usuarioID>/<int:viajeID>', methods=['GET'])
def generar_y_mostrar_agenda(usuarioID, viajeID):
    # Llama a tu función generar_agenda con los parámetros usuarioID y viajeID
    print(usuarioID, viajeID)
    agenda_service = AgendaService(getEngine())
    agenda = agenda_service.generar_agenda(usuarioID, viajeID)
    
    # Renderiza la plantilla HTML y pasa la agenda como contexto
    return render_template('agenda.html', agenda=agenda)

""" @app.route('/query', methods=['GET'])
def query():
    agenda_service = AgendaService(getEngine())

    def to_dict(obj):
        return {column.name: getattr(obj, column.name) for column in obj.__table__.columns}
    
    for viaje in agenda_service.buscarViaje(1):
        viajes = viaje.to_dict()
        print(type(viaje.to_dict()))

    return viajes """

@app.route('/generarAgendaPersonalizadas/<int:usuarioID>', methods=['GET'])
def generarYmostrarAgenda(usuarioID):
    # Llama a tu función generar_agenda con los parámetros usuarioID y viajeID
    agenda_service = AgendaService(getEngine())
    horariosPersonalizados = agenda_service.horariosDias("2023-09-01", "2023-09-06", "10:00:00", "18:00:00")

    print(horariosPersonalizados)
    """ agendaPersonalizada = agenda_service.generarAgendaPersonalizada(usuarioID,horariosPersonalizados)

    def to_dict(obj):
        return {column.name: getattr(obj, column.name) for column in obj.__table__.columns} 
    
    for agenda in agendaPersonalizada:
        agendaCreada = agenda.to_dict()
        print(type(agenda.to_dict())) """

    # Renderiza la plantilla HTML y pasa la agenda como contexto
    return {}