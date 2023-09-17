from collections import defaultdict
from flask import Flask, jsonify, render_template

import json

import googlemaps

from .models.Usuario import Usuario
from .models.ActividadCategoria import ActividadCategoria

from .models.UsuarioCategoria import UsuarioCategoria

from .models.Ciudad import Ciudad

from .models.Categoria import Categoria
from .models.Itinerario import Itinerario
from .models.Lugar import Lugar
from .models.LugarCategoria import LugarCategoria

from .utils.AlchemyEncoder import AlchemyEncoder

from .service.AgendaService import AgendaService
"""from .service.GustaService import GustaService """

from .models.Actividad import Actividad
from .models.AgendaDiaria import AgendaDiaria
from .models.Viaje import Viaje
from .bd.conexion import getSession, getEngine, Base


app = Flask(__name__)
DeDatos = getSession()
engine = getEngine()
Base.metadata.create_all(engine)

nuevoUsuario = Usuario()
nuevoViaje = Viaje()
nuevaCiudad = Ciudad()
nuevoItinerario = Itinerario()
nuevaAgendaDiaria = AgendaDiaria()
nuevoLugar = Lugar()
nuevaActividad = Actividad()
nuevaCategoria = Categoria()
nuevoCategoriaLugar = LugarCategoria()
nuevoUsuarioCategoria = UsuarioCategoria()
nuevaActividadCategoria = ActividadCategoria()

@app.route('/', methods=['GET'])
def clean_publications():
    return "Hola mundo!"

""" if __name__ == '__main__':
    app.run(debug=True) """

""" @app.route('/gustos', methods=['GET'])
def show_activity():
    gustos = GustaService().get_activities()  # Llama al método get_activities para obtener los datos
    #print (gustos)
    return render_template('gustos_detail.html', activities=gustos)
"""
@app.route('/generar_agenda/<int:usuarioID>/<int:destinoID>', methods=['GET'])
def generar_y_mostrar_agenda(usuarioID, destinoID):
    agenda_service = AgendaService(getEngine())
    agenda = agenda_service.generar_agenda(usuarioID, destinoID, '2023-01-01', '2023-01-04', '13:00:00','19:00:00')
    # Crear un diccionario para agrupar las actividades por día
    agenda_por_dia = defaultdict(list)
    for actividad_data in agenda:
        dia = actividad_data['dia']
        agenda_por_dia[dia].append(actividad_data)
    
    # Crear una lista de diccionarios serializables a JSON ordenados por día
    agenda_json = []
    for dia, actividades in sorted(agenda_por_dia.items()):
        dia_json = {
            'dia': dia.strftime('%d-%m-%Y'),
            'actividades': []
        }
        for actividad_data in actividades:
            actividad_json = {
                'id': actividad_data['actividad'].id,
                'actividad': actividad_data['actividad'].nombre,
                'lugar': actividad_data['lugar'],
                'hora_inicio': actividad_data['hora_inicio'].strftime('%H:%M:%S'),
                'hora_fin': actividad_data['hora_fin'].strftime('%H:%M:%S')
            }
            dia_json['actividades'].append(actividad_json)
        agenda_json.append(dia_json)

    # Devolver la lista de días y actividades serializadas a JSON
    return jsonify(agenda_json)

""" @app.route('/generar/agenda/ocupada/<int:usuarioID>/<int:destinoID>', methods=['GET'])
def generar_y_mostrar_agendaOcupada(usuarioID, destinoID):
    agenda_service = AgendaService(getEngine())
    ocupado = { 1 : ('17:00:00' , '19:00:00' ), 3 : ('21:00:00' , '23:00:00')}
    agenda = agenda_service.generar_agendaOcupada(usuarioID, destinoID, ocupado)

    agenda_por_dia = defaultdict(list)
    for actividad_data in agenda:
        dia = actividad_data['dia']
        agenda_por_dia[dia].append(actividad_data)
    
    agenda_json = []
    for dia, actividades in sorted(agenda_por_dia.items()):
        dia_json = {
            'dia': dia,
            'actividades': []
        }
        for actividad_data in actividades:
            actividad_json = {
                'id': actividad_data['actividad'].id,
                'nombre': actividad_data['actividad'].nombre,
                'tipo': actividad_data['actividad'].tipo,
                'hora_inicio': actividad_data['hora_inicio'].strftime('%H:%M:%S'),
                'hora_fin': actividad_data['hora_fin'].strftime('%H:%M:%S')
            }
            dia_json['actividades'].append(actividad_json)
        agenda_json.append(dia_json)

    return jsonify(agenda_json) """


""" @app.route('/query', methods=['GET'])
def query():
    agenda_service = AgendaService(getEngine())

    def to_dict(obj):
        return {column.name: getattr(obj, column.name) for column in obj.__table__.columns}
    
    for viaje in agenda_service.buscarViaje(1):
        viajes = viaje.to_dict()
        print(type(viaje.to_dict()))

    return viajes """

@app.route('/generarAgendaPersonalizadas/<int:usuarioID>/<int:destinoID>', methods=['GET'])
def generarYmostrarAgendaPersonalizada(usuarioID,destinoID):
    agenda_service = AgendaService(getEngine())
    horariosElegidos = { '2023-01-01': ('12:00:00' , '14:00:00' ), '2023-01-02': ('19:00:00' , '22:00:00')}
    agenda = agenda_service.generarAgendaPersonalizada(usuarioID, destinoID, horariosElegidos, '2023-01-01', '2023-01-04', '13:00:00','19:00:00')

    agenda_por_dia = defaultdict(list)
    for actividad_data in agenda:
        dia = actividad_data['dia']
        agenda_por_dia[dia].append(actividad_data)
    
    agenda_json = []
    for dia, actividades in sorted(agenda_por_dia.items()):
        dia_json = {
            'dia': dia,
            'actividades': []
        }
        for actividad_data in actividades:
            actividad_json = {
                'id': actividad_data['actividad'].id,
                'nombre': actividad_data['actividad'].nombre,
                'lugar': actividad_data['lugar'],
                'hora_inicio': actividad_data['hora_inicio'].strftime('%H:%M:%S'),
                'hora_fin': actividad_data['hora_fin'].strftime('%H:%M:%S')
            }
            dia_json['actividades'].append(actividad_json)
        agenda_json.append(dia_json)

    return jsonify(agenda_json) 
"""
@app.route('/lugar', methods=['GET'])
def placesRoutes():

    gmaps = googlemaps.Client(key='AIzaSyCNGyJScqlZHlbDtoivhNaK77wvy4AlSLk')

    return gmaps.places(query="restaurant",location= (-42.6852871,-65.3535526), radius=3000) 
    
    # Geocoding an address
    #geocode_result = gmaps.geocode('1600 , Mountain View, CA')

    # Look up an address with reverse geocoding
    reverse_geocode_result = gmaps.reverse_geocode((-42.6852871,-65.3535526))

    # Request directions via public transit
    now = datetime.now() """
"""  directions_result = gmaps.directions("Sydney Town Hall",
                                        "Parramatta, NSW",
                                        mode="transit",
                                        departure_time=now)

    # Validate an address with address validation
    addressvalidation_result =  gmaps.addressvalidation(['1600 Amphitheatre Pk'], 
                                                        regionCode='US',
                                                        locality='Mountain View', 
                                                        enableUspsCass=True) """


#schedule_automatic_trains()