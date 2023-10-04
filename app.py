from collections import defaultdict

import requests
from bs4 import BeautifulSoup

from .models.ActividadAgenda import ActividadAgenda
from .service.AgendaValidaciones import AgendaValidaciones
from flask import Flask, jsonify, render_template, request

import googlemaps

from .consultas import obtenerDirecciones, validacionTransporte

from .models.Usuario import Usuario
from .models.ActividadCategoria import ActividadCategoria
from .models.AgendaViaje import AgendaViaje

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
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
DeDatos = getSession()
engine = getEngine()
Base.metadata.create_all(engine)

nuevoUsuario = Usuario()
nuevoViaje = Viaje()
nuevaCiudad = Ciudad()
nuevoItinerario = Itinerario()
nuevaAgendaDiaria = AgendaDiaria()
nuevaAgendaViaje = AgendaViaje()
nuevoLugar = Lugar()
nuevaActividad = Actividad()
nuevaCategoria = Categoria()
nuevaActividadAgenda = ActividadAgenda()
nuevoCategoriaLugar = LugarCategoria()
nuevoUsuarioCategoria = UsuarioCategoria()
nuevaActividadCategoria = ActividadCategoria()

@app.route('/', methods=['GET'])
def clean_publications():
    return "Hola mundo!"

""" if __name__ == '__main__':
    app.run(debug=True) """

def serialize_timedelta(td):
    return str(td)

@app.route('/generar_agenda/<int:usuarioID>/<int:destinoID>/<fechaInicio>/<fechaFin>/<transporte>/<horaInicio>/<horaFin>'
            , methods=['GET'])#'POST'])
def generar_y_mostrar_agenda(usuarioID, destinoID, fechaInicio, fechaFin, transporte, horaInicio, horaFin):
    agenda_service = AgendaService(getEngine())
    print(transporte)
    try:
        AgendaValidaciones(getEngine()).validacionFecha(fechaInicio, fechaFin)
        AgendaValidaciones(getEngine()).validacionHora(horaInicio, horaFin)
        validacionTransporte(-42.767470, -65.036549, transporte)
    except ValueError as e:
        error_message = str(e)
        response = jsonify({'error': error_message})
        response.status_code = 400
        response.headers['Content-Type'] = 'application/json'  # Establece el tipo de contenido como JSON
        return response
    
    # data = request.get_json()

    # ocupados = data.get('horariosOcupado')
    # elegidos = data.get('horariosActividad')

    # horariosOcupados = defaultdict(list)
    # horariosElegidos = defaultdict(tuple)

    # for item in ocupados:
    #     dia = item['dia']
    #     hora_desde = item['horaDesdeOcupado']
    #     hora_hasta = item['horaHastaOcupado']
    #     hora_desde += ':00'
    #     hora_hasta += ':00'
    #     horariosOcupados[dia].append((hora_desde, hora_hasta))

    # # Procesar los datos de 'elegidos'
    # for item in elegidos:
    #     if dia != 'Horario General':
    #         dia = item['dia']
    #         hora_desde = item['horaDesdeActividad']
    #         hora_hasta = item['horaHastaActividad']
    #         hora_desde += ':00'
    #         hora_hasta += ':00'
    #         horariosElegidos[dia] = (hora_desde, hora_hasta)

    # horariosOcupados = dict(horariosOcupados)
    # horariosElegidos = dict(horariosElegidos)

    # print('ócupados: ',horariosOcupados)
    # print('elegidos: ', horariosElegidos)

    horariosOcupados = {
        '2023-01-02': [('14:00:00', '16:00:00'), ('20:00:00', '22:00:00')],
        '2023-01-05': [('21:00:00', '23:00:00')]
    }
    horariosElegidos = { '2023-01-01': ('12:00:00' , '14:00:00' ), '2023-01-03': ('19:00:00' , '22:00:00')} 
    
    print(transporte)
    agenda = agenda_service.generarAgendaDiaria(usuarioID, destinoID, horariosElegidos, horariosOcupados, fechaInicio, fechaFin, horaInicio,horaFin, transporte)
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
                'hora_fin': actividad_data['hora_fin'].strftime('%H:%M:%S'),
            }
            dia_json['actividades'].append(actividad_json)
        agenda_json.append(dia_json)

    
    agendaNueva = agenda_service.saveAgenda(usuarioID, destinoID, fechaInicio, fechaFin, horaInicio, horaFin,dia,agenda_json)
        
    # Devolver la lista de días y actividades serializadas a JSON
    return jsonify(agenda_json)




# @app.route('/generarAgenda/<int:usuarioID>/<int:destinoID>/<fechaInicio>/<fechaFin>/<horaInicio>/<horaFin>'
#             , methods=['GET'])
# def generarMostrarAgenda(usuarioID, destinoID, fechaInicio, fechaFin, horaInicio, horaFin):
#     agenda_service = AgendaService(getEngine())
#     try:
#         AgendaValidaciones(getEngine()).validacionFecha(fechaInicio, fechaFin)
#         AgendaValidaciones(getEngine()).validacionHora(horaInicio, horaFin)
#     except ValueError as e:
#         error_message = str(e)
#         response = jsonify({'error': error_message})
#         #print("Error:", error_message)
#         #print(response)
#         response.status_code = 400
#         response.headers['Content-Type'] = 'application/json'  # Establece el tipo de contenido como JSON
#         return response
    
#     horariosOcupados = {
#     '2023-01-02': [('14:00:00', '16:00:00'), ('20:00:00', '22:00:00')],
#     '2023-01-05': [('21:00:00', '23:00:00')]
#     }
#     horariosElegidos = { '2023-01-01': ('12:00:00' , '14:00:00' ), '2023-01-03': ('19:00:00' , '22:00:00')}
    
#     agenda = agenda_service.generarAgendaDiaria(usuarioID, destinoID, horariosElegidos, horariosOcupados, '2023-01-01', '2023-01-06', '13:00:00','23:00:00')
#     # Crear un diccionario para agrupar las actividades por día
#     agenda_por_dia = defaultdict(list)
#     for actividad_data in agenda:
#         dia = actividad_data['dia']
#         agenda_por_dia[dia].append(actividad_data)
    
#     # Crear una lista de diccionarios serializables a JSON ordenados por día
#     agenda_json = []
#     for dia, actividades in sorted(agenda_por_dia.items()):
#         dia_json = {
#             'dia': dia.strftime('%d-%m-%Y'),
#             'actividades': []
#         }
#         for actividad_data in actividades:
#             actividad_json = {
#                 'id': actividad_data['actividad'].id,
#                 'actividad': actividad_data['actividad'].nombre,
#                 'lugar': actividad_data['lugar'],
#                 'hora_inicio': actividad_data['hora_inicio'].strftime('%H:%M:%S'),
#                 'hora_fin': actividad_data['hora_fin'].strftime('%H:%M:%S'),
#             }
#             dia_json['actividades'].append(actividad_json)
#         agenda_json.append(dia_json)

#     # Devolver la lista de días y actividades serializadas a JSON
#     return jsonify(agenda_json)


@app.route('/generarAgendaPersonalizadas/<int:usuarioID>/<int:destinoID>', methods=['POST'])
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

def obtener_descripcion_lugar(nombre_lugar):
    # Utiliza la API de Wikipedia para buscar información sobre el lugar con coincidencias parciales
    url = f"https://es.wikipedia.org/w/api.php?action=query&format=json&prop=extracts&exintro=true&list=search&srsearch={nombre_lugar}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        search_results = data.get("query", {}).get("search", [])

        if search_results:
            # Obtiene el título de la primera página de resultados (la que mejor coincide)
            primer_resultado = search_results[0]
            titulo_pagina = primer_resultado.get("title")

            # Utiliza el título de la página para obtener la descripción completa
            url_pagina = f"https://es.wikipedia.org/w/api.php?action=query&format=json&prop=extracts&exintro=true&titles={titulo_pagina}"
            response_pagina = requests.get(url_pagina)

            if response_pagina.status_code == 200:
                data_pagina = response_pagina.json()
                pages = data_pagina.get("query", {}).get("pages", {})
                for page_id, page_info in pages.items():
                    if "extract" in page_info:
                        # Utiliza BeautifulSoup para eliminar etiquetas HTML
                        soup = BeautifulSoup(page_info["extract"], "html.parser")
                        text = soup.get_text()
                        return text.strip()

    # Si no se encuentra una descripción, puedes devolver un valor predeterminado o "No disponible"
    return "No disponible"

@app.route('/lugar', methods=['GET'])
def placesRoutes():

    gmaps = googlemaps.Client(key='AIzaSyCNGyJScqlZHlbDtoivhNaK77wvy4AlSLk')

    places = gmaps.places(query="places", location=(-42.767470, -65.036549), radius=4000)
    
    lugares = []
    for place in places['results']:
        lugar = {
            'id': place['place_id'],
            'imagen': place['icon'],
            'nombre': place['name'],
            'tipo': place.get('types', ['N/A'])[0],
            'direccion': place['formatted_address'],
            'valoracion': place.get('rating', 'N/A'),
        }
        lugares.append(lugar)
    
        # Ordenar la lista de lugares por valoración (rating) de mayor a menor
    lugares = sorted(lugares, key=lambda x: x['valoracion'], reverse=True)

    return jsonify(lugares)

@app.route('/lugar/<id>', methods=['GET'])
def lugarEspecifico(id):
    gmaps = googlemaps.Client(key='AIzaSyCNGyJScqlZHlbDtoivhNaK77wvy4AlSLk')

    place = gmaps.place(place_id=id)

    if 'result' in place:
        place = place['result']
        photo_reference = place.get('photos', [{}])[0].get('photo_reference', None)

        if photo_reference:
            # Construye la URL de la imagen utilizando la referencia de la foto
            imagen_url = f'https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key=AIzaSyCNGyJScqlZHlbDtoivhNaK77wvy4AlSLk'

        lugar = {
            'nombre': place['name'],
            'imagen': imagen_url if photo_reference else 'N/A',
            'tipo': place.get('types', ['N/A'])[0],
            'valoracion': place.get('rating', 'N/A'),
            'direccion': place['formatted_address'],
            'latitud': place.get('geometry', {}).get('location', {}).get('lat', 'N/A'),
            'longitud': place.get('geometry', {}).get('location', {}).get('lng', 'N/A'),
            'horarios': place.get('opening_hours', {}).get('weekday_text', 'N/A'),
            'descripcion': obtener_descripcion_lugar(place['name']), 
            'website': place.get('website', None)
        }
        return jsonify(lugar)
    else:
        return jsonify({'error': 'Place not found'})


@app.route('/agendaCreada/<int:usuarioID>' ,methods = ['GET'])
def getAgenda(usuarioID):
    # Leer el json recibido
    # agenda = request.get_json()

    agendaService = AgendaService(getEngine())

    agendaUsuario = agendaService.getAgenda(usuarioID)
  
    return str(agendaUsuario)


@app.route('/directions', methods=['GET'])
def directions():
    origen = request.args.get('origen') 
    destino = request.args.get('destino')
    transporte = request.args.get('transporte', 'driving').strip()

    # Llama a la función obtenerDirecciones desde direcciones.py
    resultado = obtenerDirecciones(origen, destino, transporte)

    return resultado

@app.route('/mostrar_mapa', methods=['GET'])
def mostrar_mapa():
    return render_template('mapa.html') 

"""    
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
