from collections import defaultdict
from datetime import datetime
import dbm

from .PruebaIA import PruebaIA

from .service.ActividadFavoritaService import ActividadFavoritaService

from .service.LugarFavoritoService import LugarFavoritoService

from .repository.AgendaRepository import AgendaRepository

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

from .models.CiudadCategoria import CiudadCategoria
from .models.ActividadAgenda import ActividadAgenda
from .models.Usuario import Usuario
from .models.ActividadCategoria import ActividadCategoria
from .models.AgendaViaje import AgendaViaje
from .models.UsuarioCategoria import UsuarioCategoria
from .models.Ciudad import Ciudad
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
nuevoCategoriaCiudad = CiudadCategoria()
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

@app.route('/generarprueba/<int:usuarioID>/<int:destinoID>',methods=['GET'])
def mostrarDistancia(usuarioID, destinoID):
    with Session(getEngine()) as session:
        agenda_repo = AgendaRepository(session)
        agenda_service = AgendaService(getEngine())
        actividadIds = agenda_repo.buscarActividad(1, 1)

        print(actividadIds)

        listaInicial = []
        listaInicial.append(actividadIds[0][0])
        cerca = agenda_service.calculoDeDistancias(
            1, 1, actividadIds[0][0], actividadIds[0][0], actividadIds)
        listaInicial.append(cerca)
        for i in range(0, len(actividadIds)):
            cerca = agenda_service.calculoDeDistancias(
                1, 1, listaInicial[-1], listaInicial[-2], actividadIds)
            listaInicial.append(cerca)
            print("inicial ", listaInicial)

    return listaInicial



@app.route('/getGustosUsuario/<int:usuarioID>',methods=['GET'])
def getFavoritos(usuarioID):
    lugarFavoritoService = LugarFavoritoService(getEngine())

    gustos = lugarFavoritoService.gustosUsuario(usuarioID)    
    
    favoritosJson = []
    
    for gusto in gustos:
        favorito= {
            "lugar" : str(gusto[0]),
            "ciudad" : str(gusto[1]),
            "usuario":str(gusto[2]),
            "like":str(gusto[3]),
        }

        favoritosJson.append(favorito)
    return jsonify(favoritosJson)

@app.route('/eliminarActividadesAgenda/<int:actividadID>/<int:AgendaViajeID>',methods=['DELETE'])
def EliminarActividad(actividadID, AgendaViajeID):
    if request.method == 'DELETE':
        agenda_service = AgendaService(getEngine())

        agenda_service.eliminarActividadAgeenda(actividadID,AgendaViajeID)

        return 'actividades de agenda: elimino?'
    else:
        return 'no'

@app.route('/recomendacionIA/<int:usuarioID>',methods=['GET'])
def recomendacion(usuarioID):
    recomendaciones = PruebaIA(getEngine())
    recomendacionesIA = recomendaciones.cargadoDeIA(usuarioID)

    recomendaciones_json = []
    for actividad in recomendacionesIA:
        recomendacion_dict = {
            'id': actividad.id,
            'nombre_actividad': actividad.nombre,
            'valoracion' : actividad.valoracion,
            'duracion' : actividad.duracion.strftime("%H:%M:%S"),
            'id_lugar' : actividad.id_lugar
        }
        recomendaciones_json.append(recomendacion_dict)
    
    return jsonify(recomendaciones_json)

@app.route('/like/<int:usuarioID>',methods=['POST'])
def like(usuarioID):
    lugarFavoritoService = LugarFavoritoService(getEngine())
    lugar = request.get_json()

    lugarFavoritoService.agregarGusto(usuarioID,lugar)    

    return '{ "data": "Gusto Actualizado" }'

@app.route('/likeActividad/<int:usuarioID>',methods=['POST'])
def likeActividad(usuarioID):
    actividadFavoritaService = ActividadFavoritaService(getEngine())
    actividad = request.get_json()

    actividadFavoritaService.agregarGustoActividad(usuarioID,actividad)    

    return '{ "data": "Gusto Actividad Actualizado" }'

@app.route('/dislike/<int:usuarioID>',methods=['POST'])
def dislike(usuarioID):
    lugarFavoritoService = LugarFavoritoService(getEngine())
    lugar = request.get_json()
    print("Lugar --> ",str(lugar))
    
    lugarFavoritoService.quitarGusto(usuarioID,lugar)    

    return '{ "data": "Gusto Actualizado" }'

@app.route('/dislikeActividad/<int:usuarioID>',methods=['POST'])
def dislikeActividad(usuarioID):
    actividadFavoritaService = ActividadFavoritaService(getEngine())
    actividad = request.get_json()
    print("Actividad --> ",str(actividad))
    
    actividadFavoritaService.quitarGustoActividad(usuarioID,actividad)    

    return '{"data": "Gusto  Actividad Actualizado" }'

@app.route('/generar_agenda/<int:usuarioID>', methods=['POST'])
def generar_y_mostrar_agenda(usuarioID):
    with Session(getEngine()) as session:
        agenda_service = AgendaService(getEngine())
        data = request.get_json()

        destino = data.get('destino')
    
        if destino is None or destino.get('nombre') == '':
            error_message = "Se debe ingresar el destino del viaje"
            response = jsonify({"error":error_message})
            response.status_code = 400
            response.headers['Content-Type'] = 'application/json'
            print(response)
            return response

        gmaps = googlemaps.Client(key='AIzaSyCNGyJScqlZHlbDtoivhNaK77wvy4AlSLk')

        resultado = gmaps.places(query=destino.get('nombre')+' '+destino.get('pais'))
        if 'results' in resultado:
            primer_resultado = resultado['results'][0]
            ciudadRecibido = LugarRepository(
                session).getCiudad(primer_resultado['place_id'])
            
            if ciudadRecibido:
                destino = ciudadRecibido.id
            else:
                ciudad = {
                    'id': primer_resultado['place_id'],
                    'nombre': primer_resultado['name'],
                    'latitud': destino.get('latitud'),
                    'longitud': destino.get('longitud')
                }
                lugarService = LugarService(getEngine())
                lugarService.guardarCiudad(ciudad)
                lugarRecibido = LugarRepository(session).getCiudad(primer_resultado['place_id'])   
                destino = lugarRecibido.id

        #destino = 1
        #destino = int(destino)
        fechaInicio = str(data.get('fechaDesde'))
        print("fechaDesde -->"+fechaInicio)
        fechaFin = str(data.get('fechaHasta'))
        horaInicio = data.get('horarioGeneral')['horaDesde'] + ':00'
        horaFin = data.get('horarioGeneral')['horaHasta'] + ':00'
        transporte = data.get('transporte')

        try:
            AgendaValidaciones(getEngine()).validacionFecha(fechaInicio, fechaFin)
            AgendaValidaciones(getEngine()).validacionHora(horaInicio, horaFin)
            validacionTransporte(-42.767470, -65.036549, transporte)
        except ValueError as e:
            error_message = str(e)
            response = jsonify({"error":error_message})
            response.status_code = 400
            response.headers['Content-Type'] = 'application/json'  # Establece el tipo de contenido como JSON
            return response
        
        horariosEspecificos = {}
        for horarioEspecifico in data.get('horariosEspecificos'):
            horariosEspecificos[horarioEspecifico['dia']] = \
                (horarioEspecifico['horaDesde']+':00',horarioEspecifico['horaHasta']+':00')

        horariosOcupados = {}
        for horarioOcupado in data.get('horariosOcupados'):
            horariosOcupados[horarioOcupado['dia']] = []
            for horario in horarioOcupado['horarios']:
                horaDesde = horario['horaDesde'] + ':00'
                horaHasta = horario['horaHasta'] + ':00'
                horariosOcupados[horarioOcupado['dia']].append((horaDesde, horaHasta))

        agenda = agenda_service.generarAgendaDiaria(usuarioID, destino, horariosEspecificos, horariosOcupados, fechaInicio, fechaFin, horaInicio,horaFin, transporte)

        agenda_por_dia = defaultdict(list)
        for actividad_data in agenda:
            dia = actividad_data['dia']
            agenda_por_dia[dia].append(actividad_data)

        agendaJSON = []
        for dia, actividades in sorted(agenda_por_dia.items()):
            dia_json = {
                'dia': dia.strftime('%Y-%m-%d'),
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

            
            agendaJSON.append(dia_json)

        agendaNueva = agenda_service.saveAgenda(usuarioID, destino, fechaInicio, fechaFin, horaInicio, horaFin,agendaJSON)
        print(agendaJSON)
        return jsonify(agendaJSON)

@app.route('/ciudades', methods=['GET'])
def obtenerCiudades():
    with Session(getEngine()) as session:
        ciudadesQuery = CiudadRepository(session).getCiudades()

        ciudades = []
        
        for ciudad in ciudadesQuery:
            ciudad_data = {
                'id': ciudad.id,
                'nombre': ciudad.nombre
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

@app.route('/lugarBasico', methods=['GET'])  #DE ESTE OBTENEMOS MAS INFORMACION COMO FOTOS Y OPINIONES
def placesRoutesBasico():
    lugar_id = request.args.get('place_id')

    gmaps = googlemaps.Client(key='AIzaSyCNGyJScqlZHlbDtoivhNaK77wvy4AlSLk')

    place_details = gmaps.place(place_id=lugar_id)

    return jsonify(place_details)


@app.route('/lugar', methods=['GET'])
def placesRoutes():
    buscarLugar = request.args.get('ciudad')
    idiomas_permitidos = ['es', 'mx', 'uy', 'ar', 'co', 'cl', 'pe', 've', 'ec', 'gt', 'cu', 'do', 'bo', 'hn', 'py', 'sv', 'ni', 'cr', 'pr']

    gmaps = googlemaps.Client(key='AIzaSyCNGyJScqlZHlbDtoivhNaK77wvy4AlSLk')

    places = gmaps.places(query=buscarLugar)
    
    ciudad = places.get('address_components', [])
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
                    'latitud': latitude,
                    'longitud': longitude,
                    'horarios': place.get('opening_hours', {}).get('weekday_text', 'N/A'),
                    #'descripcion': obtener_descripcion_lugar(place['name']), 
                    'ciudad': ciudad if ciudad else 'N/A',
                    'provincia': provincia if provincia else 'N/A',
                    'pais': pais if pais else 'N/A',
                    'website': place.get('website', None)
                }
                lugares.append(lugar)

    if not lugares:
        # Si no se encontraron lugares, crea un mensaje JSON personalizado
        mensaje = {'mensaje': 'No se encontraron lugares disponibles en esta ubicación.'}
        return jsonify(mensaje)
    
    lugares = sorted(lugares, key=lambda x: difflib.SequenceMatcher(
        None, x['nombre'], buscarLugar).ratio(), reverse=True)
    
    return jsonify(lugares)


@app.route('/lugares/cercanos', methods=['GET'])
def lugaresCercanos():
    latitud = float(request.args.get('latitud'))
    longitud = float(request.args.get('longitud'))

    gmaps = googlemaps.Client(key='AIzaSyCNGyJScqlZHlbDtoivhNaK77wvy4AlSLk')

    localizacion = (latitud, longitud)
    radio = 45000  # Radio en metros (45 km)

    # Realiza la búsqueda de lugares cercanos
    places = gmaps.places_nearby(location=localizacion, radius=radio)

    # Filtra los primeros 5 resultados si hay más disponibles
    lugares_cercanos = places['results'][:5]

    ciudad = places.get('address_components', [])
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

    lugares = []
    imagen_url = None  # Inicializa la URL de la imagen como None
    for place in lugares_cercanos:
        photo_reference = place.get('photos', [{}])[0].get('photo_reference', None)
        if photo_reference:
            imagen_url = f'https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key=AIzaSyCNGyJScqlZHlbDtoivhNaK77wvy4AlSLk'

        location = place['geometry']['location']
        latitude = location['lat']
        longitude = location['lng']

        valoracion = place.get('rating', 'N/A')
        if valoracion != 'N/A':
            valoracion = float(valoracion)
        else:
            valoracion = 0.0
        lugar = {
            'id': place['place_id'],
            'imagen': imagen_url if imagen_url else 'N/A',
            'nombre': place['name'],
            'tipo': place.get('types', ['N/A'])[0],
            'direccion': place.get('formatted_address', 'N/A'),
            'valoracion': valoracion,
            'latitud': latitude,
            'longitud': longitude,
            'horarios': place.get('opening_hours', {}).get('weekday_text', 'N/A'),
            'ciudad': ciudad if ciudad else 'N/A',
            'provincia': provincia if provincia else 'N/A',
            'pais': pais if pais else 'N/A',
            'website': place.get('website', None)
        }
        lugares.append(lugar)

    return jsonify(lugares)


@app.route('/lugarGustos/<int:usuarioId>', methods=['GET'])
def favoritos(usuarioId):
    buscarLugar = request.args.get('ciudad')
    idiomas_permitidos = ['es', 'mx', 'uy', 'ar', 'co', 'cl', 'pe', 've', 'ec', 'gt', 'cu', 'do', 'bo', 'hn', 'py', 'sv', 'ni', 'cr', 'pr']

    gmaps = googlemaps.Client(key='AIzaSyCNGyJScqlZHlbDtoivhNaK77wvy4AlSLk')

    places = gmaps.places(query=buscarLugar)
    
    ciudad = places.get('address_components', [])
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
                    'latitud': latitude,
                    'longitud': longitude,
                    'horarios': place.get('opening_hours', {}).get('weekday_text', 'N/A'),
                    #'descripcion': obtener_descripcion_lugar(place['name']), 
                    'ciudad': ciudad if ciudad else 'N/A',
                    'provincia': provincia if provincia else 'N/A',
                    'pais': pais if pais else 'N/A',
                    'website': place.get('website', None)
                }

                lugarFavorito = LugarFavoritoService(getEngine()).getLugarFavorito(usuarioId,lugar['id'])

                if(lugarFavorito != None):
                    likeLugarFavorito = lugarFavorito.like
                else:
                    likeLugarFavorito = -1

                lugarGusto = {
                    'lugar': lugar,
                    'like':  likeLugarFavorito
                }

                lugares.append(lugarGusto)

    if not lugares:
        # Si no se encontraron lugares, crea un mensaje JSON personalizado
        mensaje = {'mensaje': 'No se encontraron lugares disponibles en esta ubicación.'}
        return jsonify(mensaje)
    
    lugares = sorted(lugares, key=lambda x: difflib.SequenceMatcher(
        None, x['lugar']['nombre'], buscarLugar).ratio(), reverse=True)
    
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

@app.route('/agendaID/<int:usuarioID>/<int:agendaID>' ,methods = ['GET'])
def getAgenda(usuarioID,agendaID):
    # Leer el json recibido
    # agenda = request.get_json()
    agendaService = AgendaService(getEngine())
    agendaUsuario = agendaService.getAgenda(usuarioID,agendaID)  # Supongo que obtienes los resultados de tu función

    # Crear un diccionario para almacenar los datos en el formato deseado
    agendaRecibida = {}

    for row in agendaUsuario:
        dia = row[1].strftime("%d-%m-%Y") if row[1] else None
        actividad = {
            "id" :row[2],
            "nombre_actividad": row[3],
            "horadesde":row[4].strftime("%H:%M:%S") if row[4] else None,
            "horahasta": row[5].strftime("%H:%M:%S") if row[5] else None,
            "valoracion" : row[7],
            "duracion" : row[8].strftime("%H:%M:%S") if row[8] else None,
            "id_lugar" : row[9],
            "id_viaje": row[6]
        }

        actividadFavorita = ActividadFavoritaService(getEngine()).getActividadFavorita(usuarioID,row[2])

        if(actividadFavorita != None):
            likeActividad = actividadFavorita.like
        else:
            likeActividad = -1
        
        gustoActividad = {
            'actividad':  actividad,
            'like':  likeActividad
        }

        # Si el día ya existe en el diccionario, agregamos la actividad a la lista de actividades
        if dia in agendaRecibida:

            agendaRecibida[dia]["actividadesSugeridas"].append(gustoActividad)
        else:
            # Si el día no existe, creamos una entrada nueva
            agendaRecibida[dia] = {
                "dia": dia,
                "actividadesSugeridas": [gustoActividad]
            }

        #Convertir el diccionario en una lista de valores y devolverlo
        agendaJSON = list(agendaRecibida.values())

    return agendaJSON

@app.route('/verAgendaUsuario/<int:usuarioID>' ,methods = ['GET'])
def verAgendaUsuario(usuarioID):
# Leer el json recibido
# agenda = request.get_json()
    agendaService = AgendaService(getEngine())
    agendasUsuario = agendaService.obtenerAgendasUsuario(usuarioID)  # Supongo que obtienes los resultados de tu función
    
    agendaRecibida = agendasUsuario #.all()

    agendaActual = agendaRecibida[0][0]

    agendaJSON = {
        "destino" : str(agendaRecibida[0][8]),
        "fechaDesde": str(agendaRecibida[0][6] if agendaRecibida[0][6] else None),
        "fechaHasta": str(agendaRecibida[0][7] if agendaRecibida[0][7] else None),
        "diaViaje": []
    }

    # for diaViaje in agendaRecibida:
    #     for actividad in agendaRecibida:
    #         diaViajeJson = {
    #             """ "fecha": diaViaje[1],
    #             "actividades"={
    #                 "nombre" = agendaRecibida[] """
    #             }
    #             #"id_agenda": diaViaje[0]
        

    #     agendaJSON['diaViaje'].append(diaViajeJson)

    # agendaRecibida = {}


    for row in agendasUsuario:
        for row in agendaRecibida:
            print("row ", row)
            actividadRepo = agendaService.obtenerActividadAgenda(row[2], row[0])
            dia = row[1].strftime("%d-%m-%Y") if row[1] else None
            
            actividad = {
                "id_agenda": row[0],
                "nombre_actividad": row[3],
                # row[4].strftime("%H:%M:%S") if row[4] else None,
                "horaDesde": actividadRepo.horadesde.strftime("%H:%M:%S") if actividadRepo.horadesde else None,
                "horaHasta": actividadRepo.horahasta.strftime("%H:%M:%S") if actividadRepo.horahasta else None #row[5].strftime("%H:%M:%S") if row[5] else None,
            }

            # Si el día ya existe en el diccionario, agregamos la actividad a la lista de actividades
            if dia in agendaRecibida:
                agendaJSON['diaViaje'].append(actividad)
            else:
                # Si el día no existe, creamos una entrada nueva
                agendaJSON[dia] = {
                    "dia": dia,
                    "actividades": [actividad]
                }

 

    return jsonify(agendaJSON)

@app.route('/agendas/<int:usuarioID>' ,methods = ['GET'])
def verAgendas(usuarioID):
    agendaService = AgendaService(getEngine())
    agendasUsuario = agendaService.obtenerAgendasUsuarioConDestino(usuarioID)

    agendaJSON = []
    
    for agendaUsuario in agendasUsuario:
        agenda = {
            "destino": str(agendaUsuario[2]),
            "fechaDesde": str(agendaUsuario[0]),
            "fechaHasta": str(agendaUsuario[1]),
            "idAgendaViaje" :str(agendaUsuario[3])
        }
        agendaJSON.append(agenda)

    return jsonify(agendaJSON)

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
