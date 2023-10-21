from collections import defaultdict
import dbm

from .repository.LugarRepository import LugarRepository

from .models.Horario import Horario
from .service.LugarService import LugarService

from .models.LugaresFavoritos import LugaresFavoritos
from .repository.CiudadRepository import CiudadRepository
from sqlalchemy.orm import Session

import requests
from bs4 import BeautifulSoup

from .service.AgendaValidaciones import AgendaValidaciones
from flask import Flask, jsonify, render_template, request
from geopy.geocoders import Nominatim

import googlemaps
import json
from .consultas import obtenerDirecciones, validacionTransporte

from .models.ActividadAgenda import ActividadAgenda
from .models.Usuario import Usuario
from .models.ActividadCategoria import ActividadCategoria
from .models.AgendaViaje import AgendaViaje
from .models.UsuarioCategoria import UsuarioCategoria
from .models.Ciudad import Ciudad
from .models.Provincia import Provincia
from .models.Pais import Pais
from .models.Categoria import Categoria
from .models.Itinerario import Itinerario
from .models.Lugar import Lugar
from .models.LugarCategoria import LugarCategoria
from .service.AgendaService import AgendaService
from .models.Actividad import Actividad
from .models.AgendaDiaria import AgendaDiaria
from .models.Viaje import Viaje

from .bd.conexion import getSession, getEngine, Base
from flask_cors import CORS
import difflib

from .models.ActividadesFavoritas import ActividadesFavoritas

app = Flask(__name__)
CORS(app)
DeDatos = getSession()
engine = getEngine()
Base.metadata.create_all(engine)

nuevoUsuario = Usuario()
nuevoViaje = Viaje()
nuevoPais = Pais()
nuevaProvincia = Provincia()
nuevaCiudad = Ciudad()
nuevoItinerario = Itinerario()
nuevaAgendaDiaria = AgendaDiaria()
nuevaAgendaViaje = AgendaViaje()
nuevoHorario = Horario()
nuevoLugar = Lugar()
nuevaActividad = Actividad()
nuevoGustoActividad = ActividadesFavoritas()
nuevoGustoLugar = LugaresFavoritos()
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

@app.route('/generarprueba/<int:usuarioID>/<int:destinoID>'
            , methods=['GET'])
def mostrarDistancia(usuarioID, destinoID):
    agenda_service = AgendaService(getEngine())

    distancias = agenda_service.calculoDeDistancias(1,1, [])
     
    return distancias

@app.route('/generar_agenda/<int:usuarioID>/<int:destinoID>/<fechaInicio>/<fechaFin>/<transporte>/<horaInicio>/<horaFin>'
            , methods=['POST'])
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
    
    data = request.get_json()

    ocupados = data.get('horariosOcupado')
    elegidos = data.get('horariosActividad')

    horariosOcupados = defaultdict(list)
    horariosElegidos = defaultdict(tuple)

    for item in ocupados:
        dia = item['dia']
        hora_desde = item['horaDesdeOcupado']
        hora_hasta = item['horaHastaOcupado']
        hora_desde += ':00'
        hora_hasta += ':00'
        horariosOcupados[dia].append((hora_desde, hora_hasta))

    # Procesar los datos de 'elegidos'
    for item in elegidos:
        if dia != 'Horario General':
            dia = item['dia']
            hora_desde = item['horaDesdeActividad']
            hora_hasta = item['horaHastaActividad']
            hora_desde += ':00'
            hora_hasta += ':00'
            horariosElegidos[dia] = (hora_desde, hora_hasta)

    horariosOcupados = dict(horariosOcupados)
    horariosElegidos = dict(horariosElegidos)

    print('ócupados: ',horariosOcupados)
    print('elegidos: ', horariosElegidos)
    
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
    agendaNueva = agenda_service.saveAgenda(usuarioID, destinoID, fechaInicio, fechaFin, horaInicio, horaFin,agenda_json)

    
        
    # Devolver la lista de días y actividades serializadas a JSON
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

@app.route('/ciudades', methods=['GET'])
def obtenerCiudades():
    with Session(getEngine()) as session:
        ciudadesQuery = CiudadRepository(session).getCiudades()

        ciudades = []
        
        for ciudad in ciudadesQuery:
            ciudad_data = {
                'nombre': ciudad.nombre  # Accede a la propiedad 'nombre' de la instancia de Ciudad
            }
            ciudades.append(ciudad_data)

        return jsonify(ciudades)
    
@app.route('/lugares', methods=['GET'])
def lugares():
    with Session(getEngine()) as session:
        lugarRepo = LugarRepository(session).getLugares()

        lugares = []
        for lugar in lugarRepo:
            lugar_data = {
                'nombre': lugar.nombre,
                'codigo': lugar.codigo
            }
            lugares.append(lugar_data)

    return lugares

@app.route('/lugar', methods=['GET'])
def placesRoutes():
    buscarLugar = request.args.get('ciudad')
    idiomas_permitidos = ['es', 'mx', 'uy', 'ar', 'co', 'cl', 'pe', 've', 'ec', 'gt', 'cu', 'do', 'bo', 'hn', 'py', 'sv', 'ni', 'cr', 'pr']

    gmaps = googlemaps.Client(key='AIzaSyCNGyJScqlZHlbDtoivhNaK77wvy4AlSLk')

    places = gmaps.places(query=buscarLugar)
    
    lugares = []
    for place in places['results']:
        location = place['geometry']['location']
        latitude = location['lat']
        longitude = location['lng']

        geolocator = Nominatim(user_agent="TravleExplore-proyectoUni")
        location_info = geolocator.reverse((latitude, longitude), exactly_one=True)
        # Verificar si la información de ubicación está disponible
        if location_info and location_info.raw:
            country_code = location_info.raw.get('address', {}).get('country_code', '').lower()

            # Comprobar si el código del país está en la lista de idiomas permitidos
            print(country_code)
            if country_code in idiomas_permitidos:

                valoracion = place.get('rating', 'N/A')
                if valoracion != 'N/A':
                    valoracion = float(valoracion)
                else:
                    valoracion = 0.0
                lugar = {
                    'id': place['place_id'],
                    'imagen': place['icon'],
                    'nombre': place['name'],
                    'tipo': place.get('types', ['N/A'])[0],
                    'direccion': place['formatted_address'],
                    'valoracion': valoracion,
                }
                lugares.append(lugar)

    if not lugares:
        # Si no se encontraron lugares, crea un mensaje JSON personalizado
        mensaje = {'mensaje': 'No se encontraron lugares disponibles en esta ubicación.'}
        return jsonify(mensaje)
    
    lugares = sorted(lugares, key=lambda x: difflib.SequenceMatcher(
        None, x['nombre'], buscarLugar).ratio(), reverse=True)
    
    return jsonify(lugares)

@app.route('/lugar/<id>', methods=['GET']) #guardar aca, si el lugar ya esta no guardar(query con pais provincia ciudad)
def lugarEspecifico(id):
    gmaps = googlemaps.Client(key='AIzaSyCNGyJScqlZHlbDtoivhNaK77wvy4AlSLk')

    place = gmaps.place(place_id=id)

    if 'result' in place:
        place = place['result']
        photo_reference = place.get('photos', [{}])[0].get('photo_reference', None)

        if photo_reference:
            # Construye la URL de la imagen utilizando la referencia de la foto
            imagen_url = f'https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key=AIzaSyCNGyJScqlZHlbDtoivhNaK77wvy4AlSLk'

        ciudad = place.get('address_components', [])
        provincia = None
        pais = None

        for component in ciudad:
            types = component.get('types', [])
            if 'locality' in types:
                ciudad = component.get('long_name')
            elif 'administrative_area_level_1' in types:
                provincia = component.get('long_name')
            elif 'country' in types:
                pais = component.get('long_name')

        lugar = {
            'id' : id,
            'nombre': place['name'],
            'imagen': imagen_url if photo_reference else 'N/A',
            'icono': place['icon'],
            'tipo': place.get('types', ['N/A'])[0],
            'valoracion': place.get('rating', 'N/A'),
            'direccion': place['formatted_address'],
            'latitud': place.get('geometry', {}).get('location', {}).get('lat', 'N/A'),
            'longitud': place.get('geometry', {}).get('location', {}).get('lng', 'N/A'),
            'horarios': place.get('opening_hours', {}).get('weekday_text', 'N/A'),
            #'descripcion': obtener_descripcion_lugar(place['name']), 
            'ciudad': ciudad if ciudad else 'N/A',
            'provincia': provincia if provincia else 'N/A',
            'pais': pais if pais else 'N/A',
            'website': place.get('website', None)
        }

        LugarService(getEngine()).guardarSitio(lugar)
        return jsonify(lugar)
    else:
        return jsonify({'error': 'Place not found'})


@app.route('/agendaCreada/<int:usuarioID>' ,methods = ['GET'])
def getAgenda(usuarioID):
    # Leer el json recibido
    # agenda = request.get_json()
    agendaService = AgendaService(getEngine())
    agendaUsuario = agendaService.getAgenda(usuarioID)  # Supongo que obtienes los resultados de tu función

    # Crear un diccionario para almacenar los datos en el formato deseado
    agenda_data = {}

    for row in agendaUsuario:
        dia =  row[1].strftime("%Y-%m-%d") if row[1] else None
        actividad = {
            "nombre_actividad": row[3],
            "horaInicio":row[4].strftime("%H:%M:%S") if row[4] else None,
            "horaFin": row[5].strftime("%H:%M:%S") if row[5] else None,
        }

        # Si el día ya existe en el diccionario, agregamos la actividad a la lista de actividades
        if dia in agenda_data:
            agenda_data[dia]["actividades"].append(actividad)
        else:
            # Si el día no existe, creamos una entrada nueva
            agenda_data[dia] = {
                "dia": dia,
                "actividades": [actividad]
            }

        #Convertir el diccionario en una lista de valores y devolverlo
        agenda_json = list(agenda_data.values())

    return agenda_json


@app.route('/verAgendaUsuario/<int:usuarioID>' ,methods = ['GET'])
def verAgendaUsuario(usuarioID):
# Leer el json recibido
# agenda = request.get_json()
    agendaService = AgendaService(getEngine())
    agendasUsuario = agendaService.obtenerAgendasUsuario(usuarioID)  # Supongo que obtienes los resultados de tu función
    
    agenda_data = agendasUsuario.all()

    agendaActual = agenda_data[0][0]

    agenda_json = {
        "destino" : str(agenda_data[0][8]),
        "fechaDesde": str(agenda_data[0][6] if agenda_data[0][6] else None),
        "fechaHasta": str(agenda_data[0][7] if agenda_data[0][7] else None),
        "diaViaje": []
    }

    for diaViaje in agenda_data:
        diaViajeJson = {
            "fecha": diaViaje[1],
            "id_agenda": diaViaje[0]
        }

        agenda_json['diaViaje'].append(diaViajeJson)

    '''agenda_data = {}


    for row in agendasUsuario:
        dia =  row[1].strftime("%Y-%m-%d") if row[1] else None
        
        actividad = {
            "id_agenda": row[0],
            "nombre_actividad": row[3],
            "horaInicio":row[4].strftime("%H:%M:%S") if row[4] else None,
            "horaFin": row[5].strftime("%H:%M:%S") if row[5] else None,
        }

        # Si el día ya existe en el diccionario, agregamos la actividad a la lista de actividades
        if dia in agenda_data:
            agenda_data[dia]["actividades"].append(actividad)
        else:
            # Si el día no existe, creamos una entrada nueva

            agenda_data[dia] = {
                "dia": dia,
                "actividades": [actividad]
            }

        # Convertir el diccionario en una lista de valores y devolverlo
        agendas_json = list(agenda_data.values())'''

    return jsonify(agenda_json)

       
@app.route('/agendas/<int:usuarioID>' ,methods = ['GET'])
def verAgendas(usuarioID):
    agendaService = AgendaService(getEngine())
    agendasUsuario = agendaService.obtenerAgendasUsuarioConDestino(usuarioID)

    agenda_json = []
    
    for agendaUsuario in agendasUsuario:
        agenda = {
            "destino": str(agendaUsuario[2]),
            "fechaDesde": str(agendaUsuario[0]),
            "fechaHasta": str(agendaUsuario[1])
        }
        agenda_json.append(agenda)

    return jsonify(agenda_json)



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
