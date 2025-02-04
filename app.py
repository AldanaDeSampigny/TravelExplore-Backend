from collections import defaultdict
import uuid

from .service.ActividadesService import ActividadesService 
from .service.CategoriaService import CategoriaService

from .Entrenamiento import entrenarIA
from .service.UsuarioService import UsuarioService

from .PruebaIA import PruebaIA
from .generadorRecomendaciones import GeneradorRecomendaciones
from .service.ActividadFavoritaService import ActividadFavoritaService
from .service.LugarFavoritoService import LugarFavoritoService
from .repository.AgendaRepository import AgendaRepository
from .repository.LugarRepository import LugarRepository
from .service.LugarService import LugarService

from .repository.CiudadRepository import CiudadRepository
from .repository.ActividadRepository import ActividadRepository
from sqlalchemy.orm import Session

import requests
from bs4 import BeautifulSoup

from .service.AgendaValidaciones import AgendaValidaciones
from flask import Flask, jsonify, render_template, request
from geopy.geocoders import Nominatim

import googlemaps
import json
from .consultas import obtenerDirecciones, validacionTransporte
from apscheduler.schedulers.background import BackgroundScheduler

from .models.PalabrasProhibidas import PalabrasProhibidas
from .models.Reseña import Reseña
from .models.LugaresFavoritos import LugaresFavoritos
from .models.ActividadLugar import ActividadLugar
from .models.Horario import Horario
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
from werkzeug.security import check_password_hash

from .bd.conexion import getSession, getEngine, Base
from flask_cors import CORS
import difflib
from geopy.geocoders import Nominatim
from .models.ActividadesFavoritas import ActividadesFavoritas

app = Flask(__name__)
CORS(app)
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
nuevoActividadLugar = ActividadLugar()
nuevoGustoActividad = ActividadesFavoritas()
nuevoGustoLugar = LugaresFavoritos()
nuevaCategoria = Categoria()
nuevaActividadAgenda = ActividadAgenda()
nuevoCategoriaCiudad = CiudadCategoria()
nuevoCategoriaLugar = LugarCategoria()
nuevoUsuarioCategoria = UsuarioCategoria()
nuevaActividadCategoria = ActividadCategoria()
nuevaPalabrasProhibidas = PalabrasProhibidas()
nuevaResenia = Reseña()

llave = 'AIzaSyCNGyJScqlZHlbDtoivhNaK77wvy4AlSLk'
modelo_recomendacion = None

print("Cargando modelo...")
ia = PruebaIA(getSession())
modelo_recomendacion = ia.cargadoDeIA()

print(f"Tipo de modelo_recomendacion: {type(modelo_recomendacion)}")
print(modelo_recomendacion.summary())

AgendaService(modelo_recomendacion, getSession())

generadorRecomendaciones = GeneradorRecomendaciones(modelo_recomendacion)

@app.route('/', methods=['GET'])
def clean_publications():
    return "Hola mundo!"

def entrenar_IA():
    print("Entrenamiento iniciado")
    scheduler = BackgroundScheduler()

    #schedule_thread = threading.Thread(target=schedule.run_continuously)
    scheduler.add_job(entrenarIA, 'cron',hour=23, minute=18)
    scheduler.start()

entrenar_IA()

if __name__ == '__main__':
    app.run(host="if012atur.fi.mdn.unp.edu.ar", debug=True, port=28001)

@app.route('/recomendar/<int:usuarioID>', methods=['GET'])
def recomendar(usuarioID):
    if not modelo_recomendacion:
        return jsonify({"error": "Modelo no cargado"}), 500
    
    with Session(getEngine()) as db_session:
        generador = GeneradorRecomendaciones(modelo_recomendacion, db_session)
        recomendaciones = generador.generar_recomendaciones(usuarioID)
    
    # Convertir cada recomendación a un diccionario directamente en esta parte
    recomendaciones_serializables = [
        {
            'id': actividad.id,
            'nombre': actividad.nombre,
            # Agrega otros atributos necesarios de `Actividad`
        } 
        for actividad in recomendaciones
    ]
    
    return jsonify(recomendaciones_serializables)

def serialize_timedelta(td):
    return str(td)


def ejecutar_recomendaciones_auto(usuarioID):
    with app.app_context():
        lugarRecomendacion(usuarioID)
        actividadRecomendacion(usuarioID) 

@app.route('/registrarUsuario',methods=['POST'])
def nuevoUsuario():
    with Session(getEngine()) as session:
        usuarioService = UsuarioService(getEngine())
        nuevoUsuario = request.get_json()
        
        nombreUsuario = usuarioService.getUsuarioNombre(nuevoUsuario.get('nombre'))
        print("nombre usuario", nombreUsuario)

        
        
        if(nombreUsuario != None):
            error_message = "El usuario ya existe"
            responseNombre = jsonify({"error":error_message})
            responseNombre.status_code = 401
            responseNombre.headers['Content-Type'] = 'application/json'
            return responseNombre
        else:
            if(nuevoUsuario.get('nombre') == ""):
                error_message = "El nombre de usuario no puede ser vacio"
                responseNombreVacio = jsonify({"error":error_message})
                responseNombreVacio.status_code = 402
                responseNombreVacio.headers['Content-Type'] = 'application/json'
                return responseNombreVacio
            else:
                if(nuevoUsuario.get('confirmarContrasena') != nuevoUsuario.get('contrasenia')):
                    error_message = "Las contraseñas no coniciden"
                    response = jsonify({"error":error_message})
                    response.status_code = 400
                    response.headers['Content-Type'] = 'application/json'
                    return response
                else:
                    usuarioRegistrado = usuarioService.agregarUsuario(nuevoUsuario.get('nombre'),nuevoUsuario.get('email'),nuevoUsuario.get('contrasenia')) 
                    print("id usuario registrado", usuarioRegistrado)

                    usuario = usuarioService.getUsuarioID(usuarioRegistrado)

                    nuevoUsuarioJson = {
                        "id" : usuario.id,
                        "nombre": usuario.nombre,
                        "contrasenia": usuario.contrasenia,
                        "gmail": usuario.gmail,
                        "imagen": usuario.imagen
                    }

            return  nuevoUsuarioJson
    
@app.route('/generarprueba/<int:usuarioID>/<int:destinoID>',methods=['GET'])
def mostrarDistancia(usuarioID, destinoID):
    with Session(getEngine()) as session:
        agenda_repo = AgendaRepository(session)
        agenda_service = AgendaService(modelo_recomendacion, getEngine())
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

    gustosLugar = lugarFavoritoService.gustosUsuario(usuarioID)    

    favoritosJson = []
    for gusto in gustosLugar:
        favorito= {
            "lugar" : str(gusto[0]),
            "ciudad" : str(gusto[1]),
            "usuario":str(gusto[2]),
            "like":str(gusto[3]),
            "codigo" :  str(gusto[4]),
        }

        favoritosJson.append(favorito)

    return jsonify(favoritosJson)

@app.route('/getActividadesFavoritas/<int:usuarioID>',methods=['GET'])
def getActividadesFavoritas(usuarioID):
    actividadFavoritaService = ActividadFavoritaService(getEngine())

    gustosActividad = actividadFavoritaService.getActividadesFavoritas(usuarioID)    
    
    actividadesJson = []
    for gustoActividad in gustosActividad:
        actividad = {
            "nombre_actividad" : str(gustoActividad[0]),
            "valoracion" : str(gustoActividad[1]),
            "duracion":str(gustoActividad[2]),
            "like":str(gustoActividad[4]),
        }


        actividadesJson.append(actividad)
    return jsonify(actividadesJson)
    
@app.route('/eliminarActividadesAgenda/<int:actividadID>/<int:AgendaViajeID>',methods=['DELETE'])
def EliminarActividad(actividadID, AgendaViajeID):
    if request.method == 'DELETE':
        agenda_service = AgendaService(modelo_recomendacion, getEngine())

        agenda_service.eliminarActividadAgeenda(actividadID,AgendaViajeID)

        return 'actividades de agenda: elimino?'
    else:
        return 'no'

@app.route('/recomendacionLugaresIA/<int:usuarioID>',methods=['GET'])
def lugarRecomendacion(usuarioID):
    recomendaciones = generadorRecomendaciones.generar_recomendaciones(usuarioID) or []

    actividadService = ActividadesService(getEngine())
    recomendaciones_json = [
        {
            'id': lugar.codigo,
            'nombre': lugar.nombre,
            'tipo': lugar.tipo,
            'valoracion': lugar.valoracion
        }
        for actividad in recomendaciones
        if actividad.id is not None and (lugar := actividadService.obtenerLugarActividad(actividad.id)) is not None
    ]

    return jsonify(recomendaciones_json)

@app.route('/recomendacionActividadesIA/<int:usuarioID>',methods=['GET'])
def actividadRecomendacion(usuarioID):
    recomendaciones = generadorRecomendaciones.generar_recomendaciones(usuarioID)
    
    recomendaciones_serializables = [
        {
            'id': actividad.id,
            'nombre_actividad': actividad.nombre,
            'valoracion' : actividad.valoracion,
            'duracion' : actividad.duracion.strftime("%H:%M:%S")
        } 
        for actividad in recomendaciones
    ]
    
    return jsonify(recomendaciones_serializables)


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

    return '{ }'

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
        geolocator = Nominatim(user_agent="Travel_explore")
        agenda_service = AgendaService(modelo_recomendacion, getEngine())
        data = request.get_json()

        destino = data.get('destino')
        direccionHospedaje = data.get('direccionHospedaje')
        
    
        if destino is None or destino.get('nombre') == '':
            error_message = "Se debe ingresar el destino del viaje"
            response = jsonify({"error":error_message})
            response.status_code = 400
            response.headers['Content-Type'] = 'application/json'
            print(response)
            return response

        gmaps = googlemaps.Client(key=llave)

        resultado = gmaps.places(query=destino.get('nombre')+' '+destino.get('pais'))
        #resultado = " results Puerto Madryn Argentina"
        if 'results' in resultado:
            primer_resultado = None#resultado['results'][0]
            ciudadRecibido = LugarRepository(
                session).getCiudad('ChIJ0eqih141Ar4RgkO0ECgNiR4')  # primer_resultado['place_id'])
            
            if ciudadRecibido:
                destino = ciudadRecibido.id

                direccion = direccionHospedaje + ", " +ciudadRecibido.nombre
                print("direccion ", direccion)

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

                direccion = direccionHospedaje + lugarRecibido.nombre

            ubicacion = geolocator.geocode(query=direccion, exactly_one=True)
        
            print("geolocator --> lat:", ubicacion.latitude, ", long:",ubicacion.longitude)

        fechaInicio = str(data.get('fechaDesde'))
        print("fechaDesde -->"+fechaInicio)
        fechaFin = str(data.get('fechaHasta'))
        horaInicio = data.get('horarioGeneral')['horaDesde'] + ':00'
        horaFin = data.get('horarioGeneral')['horaHasta'] + ':00'
        transporte = data.get('transporte')

        # try:
        #     AgendaValidaciones(getEngine()).validacionFecha(fechaInicio, fechaFin)
        #     AgendaValidaciones(getEngine()).validacionHora(horaInicio, horaFin)
        #     validacionTransporte(-42.767470, -65.036549, transporte)
        # except ValueError as e:
        #     error_message = str(e)
        #     response = jsonify({"error":error_message})
        #     response.status_code = 400
        #     response.headers['Content-Type'] = 'application/json'  # Establece el tipo de contenido como JSON
        #     return response
        
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

        agenda = agenda_service.generarAgendaDiaria(ubicacion, usuarioID, destino, horariosEspecificos, horariosOcupados, fechaInicio, fechaFin, horaInicio,horaFin, transporte)

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
                print("---- ACTIVIDAD DATA ----", actividad_data)
                actividad_json = {
                    'id': actividad_data['actividad'].id,
                    'actividad': actividad_data['actividad'].nombre,
                    'lugar': actividad_data['lugar'],
                    'hora_inicio': actividad_data['hora_inicio'].strftime('%H:%M:%S'),
                    'hora_fin': actividad_data['hora_fin'].strftime('%H:%M:%S'),
                }
                dia_json['actividades'].append(actividad_json)

            agendaJSON.append(dia_json)
            print("agenda json",agendaJSON)
            print("transporte ", transporte)
        agendaNueva = agenda_service.saveAgenda(usuarioID, destino, fechaInicio, fechaFin, horaInicio, horaFin,agendaJSON,transporte, direccionHospedaje)
        print("agenda cread",agendaJSON)
        return jsonify(agendaNueva)

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
    
@app.route('/lugares/por/ciudades/<int:idCiudad>', methods=['GET'])
def lugaresByCiudades(idCiudad):
    with Session(getEngine()) as session:
        lugarRepo = LugarRepository(session)

        opciones = lugarRepo.getLugaresByCiudadID(idCiudad)

        lugares = []
        for lugar in opciones:
            lugar_data = {
                'id': lugar.id,
                'nombre': lugar.nombre
            }
            lugares.append(lugar_data)

    return jsonify(lugares)

    
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

    gmaps = googlemaps.Client(key=llave)

    place_details = gmaps.place(place_id=lugar_id)

    return jsonify(place_details)

""" @app.route('/lugar', methods=['GET'])
def placesRoutes():
    buscarLugar = request.args.get('ciudad')
    idiomas_permitidos = ['es', 'mx', 'uy', 'ar', 'co', 'cl', 'pe', 've', 'ec', 'gt', 'cu', 'do', 'bo', 'hn', 'py', 'sv', 'ni', 'cr', 'pr']

    gmaps = googlemaps.Client(key=llave)

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
                print(lugar)

    if not lugares:
        # Si no se encontraron lugares, crea un mensaje JSON personalizado
        mensaje = {'mensaje': 'No se encontraron lugares disponibles en esta ubicación.'}
        return jsonify(mensaje)
    
    lugares = sorted(lugares, key=lambda x: difflib.SequenceMatcher(
        None, x['nombre'], buscarLugar).ratio(), reverse=True)
    
    return jsonify(lugares) """

@app.route('/lugares/cercanos/<int:idUsuario>/<string:kilometros>', methods=['GET'])
def lugaresCercanos(idUsuario,kilometros):
    latitud = float(request.args.get('latitud'))
    longitud = float(request.args.get('longitud'))
    tipo = request.args.get('type')

    gmaps = googlemaps.Client(key=llave)

    localizacion = (latitud, longitud)
   
    if (kilometros is not None):
        radio = int(f"{kilometros}00")
        #le agrega al numero  dos 0 al final  
        print("radio kilometros:" , radio)
        # Realiza la búsqueda de lugares cercanos
        places = gmaps.places_nearby(location=localizacion, type=tipo, radius=radio)


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
        
        lugarFavorito = LugarFavoritoService(getEngine()).getLugarFavorito(idUsuario,lugar['id'])

        print("lugar favorito", lugarFavorito)
        if(lugarFavorito != None):
            likeLugarFavorito = lugarFavorito.like
        else:
            likeLugarFavorito = -1

        lugarGusto = {
            'lugar': lugar,
            'like':  likeLugarFavorito
        }

        lugares.append(lugarGusto)
    return jsonify(lugares)

@app.route('/lugarGustos/<int:usuarioId>', methods=['GET'])
def favoritos(usuarioId):
    buscarLugar = request.args.get('ciudad')
    idiomas_permitidos = ['es', 'mx', 'uy', 'ar', 'co', 'cl', 'pe', 've', 'ec', 'gt', 'cu', 'do', 'bo', 'hn', 'py', 'sv', 'ni', 'cr', 'pr']

    gmaps = googlemaps.Client(key=llave)

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
#devuelve un lugar en pantalla 
@app.route('/lugar/<id>', methods=['GET']) #guardar aca, si el lugar ya esta no guardar(query con pais provincia ciudad)
def lugarEspecifico(id):
    gmaps = googlemaps.Client(key=llave)

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
        print(lugar)
        return jsonify(lugar)
    else:
        return jsonify({'error': 'Place not found'})

@app.route('/usuarioID/<int:ID>', methods = ['GET'])
def getUsuarioID(ID):
    usuarioService = UsuarioService(getEngine())

    usuarioAux = usuarioService.getUsuarioID(ID)

    usuario = {
        "id": usuarioAux.id,
        "nombre": usuarioAux.nombre,
        "gmail": usuarioAux.gmail,
        "contraseña": usuarioAux.contrasenia,
        "imagen": usuarioAux.imagen
    }

    return jsonify(usuario)

@app.route('/guardarGustos/<int:usuarioID>', methods=['GET'])
def guardarGustos(usuarioID):
    categoriaService = CategoriaService(getEngine())
    gustos_str = request.args.get('gustos')
    gustos = json.loads(gustos_str)
    idsGustos = []
    print('str ', gustos_str)

    try:
        nombreGustosNuevos = [gusto['nombre'] for gusto in gustos if gusto['id'] == 0]
        categoriaService.buscarGusto(usuarioID, nombreGustosNuevos)
    
        idsGustos = [gusto['id'] for gusto in gustos if gusto['id'] != 0]
        categoriaService.guardarGustos(usuarioID, idsGustos)
    except ValueError as e:
        error_message = str(e)
        response = jsonify({"error":error_message})
        response.status_code = 400
        response.headers['Content-Type'] = 'application/json'  # Establece el tipo de contenido como JSON
        return response

    return jsonify({'message': 'Gustos recibidos correctamente'})

@app.route('/categorias', methods= ['GET'])
def getCategorias():
    categoriaService = CategoriaService(getEngine())
    categoriasAux = []

    categorias = categoriaService.getCategorias()

    for cate in categorias:
        categoria = {
            "id": cate.id,
            "nombre": cate.nombre
        }
        categoriasAux.append(categoria)

    return jsonify(categoriasAux)

@app.route('/editarUsuario', methods=['POST'])
def editarUsuario():
    usuarioService = UsuarioService(getEngine())
    
    try:
        if request.is_json:
            usuario = request.json
            usuarioService.editarUsuario(usuario)

            usuarioEditado = {
                "id": usuario.get('id'),  
                "nombre": usuario.get('nombre'),
                "gmail": usuario.get('gmail'),
                "imagen": usuario.get('imagen')
            }
            return jsonify(usuarioEditado)
        else:
            return 'La solicitud no incluye datos JSON', 400
    except Exception as e:
        print(f"Error en la edición de usuario: {str(e)}")
        return 'Error en la edición de usuario', 500

@app.route('/agendaID/<int:usuarioID>/<int:agendaID>' ,methods = ['GET'])
def getAgenda(usuarioID,agendaID):
    # Leer el json recibido
    #agenda = request.get_json()
    agendaService = AgendaService(modelo_recomendacion, getEngine())
    agendaUsuario = agendaService.getAgenda(usuarioID,agendaID)  # Supongo que obtienes los resultados de tu función
    geolocator = Nominatim(user_agent="Travel_explore")
    print("agenda", agendaUsuario)
    # Crear un diccionario para almacenar los datos en el formato deseado
    agendaRecibida = {}
    agendaJSON = list()

    for row in agendaUsuario:
        idAgendaDiaria = row[0],
        dia = row[1].strftime("%d-%m-%Y") if row[1] else None,
        id_ciudad = row[11],
        nombre_ciudad = row[10],
        hospedaje = row[16],
        actividad = {
            "id" :row[2],          
            "nombre_actividad": row[3],
            "horadesde":row[4].strftime("%H:%M:%S") if row[4] else None,
            "horahasta": row[5].strftime("%H:%M:%S") if row[5] else None,
            "valoracion" : row[7],
            "duracion" : row[8].strftime("%H:%M:%S") if row[8] else None,
            "id_lugar" : row[9],
            "id_viaje": row[6],
            "tranporte"  : row[15],
            #"nombre_lugar" : row[11],
            "lugar": {
                "id": row[9],  # Ajusta según tus necesidades
                "nombre": row[12],  # Ajusta según tus necesidades
                "latitud": row[13],  # Ajusta según tus necesidades
                "longitud": row[14]
            }
        }
         # Asegúrate de extraer correctamente los valores de las tuplas
        nombre_ciudad_str = nombre_ciudad[0] if isinstance(nombre_ciudad, tuple) else nombre_ciudad
        hospedaje_str = hospedaje[0] if isinstance(hospedaje, tuple) else hospedaje

        # Concatenar hospedaje y nombre de ciudad
        direccion = f"{hospedaje_str},{nombre_ciudad_str}"

        print("direccion",direccion)
        #!seguir viendo el tema del formato ahora esta asi (direccion,)
        #!acceder a la tupla 
        #! hay que logra que quede "Villarino 1385,Puerto Madryn"
        ubicacion = geolocator.geocode(query=direccion, exactly_one=True)

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
                "idAgendaDiaria" : idAgendaDiaria,
                "dia": dia,
                "id_ciudad": id_ciudad,
                "hospedaje" :{
                    "nombre" : hospedaje,
                    "latitud": ubicacion.latitude,
                    "longitud": ubicacion.longitude,
                },
                "actividadesSugeridas": [gustoActividad]
            }

        #Convertir el diccionario en una lista de valores y devolverlo
        agendaJSON = list(agendaRecibida.values())

    return jsonify(agendaJSON)

@app.route('/modificarAgendaDiaria/<int:idAgenda>', methods=['POST'])
def modificarAgendaDiaria(idAgenda):
    with Session(getEngine()) as session:
        agenda_service = AgendaService(modelo_recomendacion, getEngine())
        data = request.get_json()
        updated_agenda = []
        obtenerAgenda = getAgendaDiaria(idAgenda,1)
        print("agrenda Diaria", obtenerAgenda)

        for actividad in data:
            lugar = actividad.get('lugar')
            otros_lugares = actividad.get('otrosLugares')
            actividadAgenda = actividad.get('actividad')

            agendadiaria = {
                'id': actividad.get('id'),
                'horaInicio': actividad.get('horaInicio'),
                'horaFin': actividad.get('horaFin'),
                'actividad': {
                    'id': actividadAgenda.get('id'),
                    'nombre': actividadAgenda.get('nombre')
                },
                'lugar': {
                    'id_lugar': lugar.get('id_lugar'),
                    'id_actividad': lugar.get('id_actividad'),
                    'nombre': lugar.get('nombre')
                },
                'otros_lugares': [
                    {
                        'id_lugar': otro_lugar.get('id_lugar'),
                        'id_actividad': otro_lugar.get('id_actividad'),
                        'nombre': otro_lugar.get('nombre')
                    } for otro_lugar in otros_lugares
                ],
                'transporte_ciudad': actividad.get('transporte_ciudad')
            }
            print("AGENDA CON FORMATO ", agendadiaria)
            agenda_service.modificar_agenda_diaria(agendadiaria)
            updated_agenda.append(agendadiaria)

        return jsonify({
            'status': 'success',
            'message': 'Agenda actualizada correctamente',
            'updated_agenda': updated_agenda
        }), 200

@app.route('/getTodoActividades', methods = ['GET'])
def getAllActividades():
    with Session(getEngine()) as session:
        actividadQuery = ActividadRepository(session).getActividades()

        actividades = []
        
        for actividad in actividadQuery:
            actividad_data = {
                'id': actividad.id,
                'nombre': actividad.nombre
            }
            actividades.append(actividad_data)

        return jsonify(actividades)

@app.route('/getAgendaDiaria/<int:idAgenda>/<int:idCiudad>', methods = ['GET'])
def getAgendaDiaria(idAgenda, idCiudad):
    agendaService = AgendaService(modelo_recomendacion, getEngine())
    agendaDiaria = agendaService.obtenerAgendaDiaria(idAgenda, idCiudad)

    print("--- agendaDiaria --- ", agendaDiaria) 

    agenda = []
    actividades_dict = {}

    for row in agendaDiaria:
        print("ROW COMPLETO: ",row)
        id_actividad = row[3]
        print("ciudad", row[9])
        if id_actividad not in actividades_dict:
            actividades_dict[id_actividad] = {
                "id": row[0],
                "horaInicio": row[1].strftime('%H:%M:%S'),
                "horaFin": row[2].strftime('%H:%M:%S'),
                "actividad":{
                    'id': row[3],
                    'nombre': row[4]
                },
                "lugar": None,
                "otrosLugares": [],
                "transporte_ciudad": row[8],
                "nombreCiudad" : row[9]
            }
        idLugarSeleccionado = row[10] 

        lugarAgenda = {
            "id_actividad": row[3],
            "id_lugar": row[5],
            "nombre": row[6],
        }
        actividades_dict[id_actividad]["otrosLugares"].append(lugarAgenda)
        if lugarAgenda["id_lugar"] == idLugarSeleccionado:
            actividades_dict[id_actividad]["lugar"] = lugarAgenda
    
    for id_actividad, actividad in actividades_dict.items():
        agenda.append(actividad)

    print("&&&& AGENDA:",agenda)
    print(type(agenda))
    return jsonify(agenda)

@app.route('/agendas/<int:usuarioID>' ,methods = ['GET'])
def verAgendas(usuarioID):
    agendaService = AgendaService(modelo_recomendacion, getEngine())
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

@app.route('/buscarUsuario', methods=['POST'])
def usuarioIniciado():
    usuario = request.get_json()
    usuarioService = UsuarioService(getEngine())
    nombre = usuario.get('nombre')


    contrasenia = usuario.get('contrasenia')
    usuarioIniciado = usuarioService.getUsuarioIniciado(nombre, contrasenia)
    print("usuario", usuarioIniciado.nombre)

    if usuarioIniciado is None:
            error_message = "El Usuario o Contraseña son incorrectos"
            response = jsonify({"error":error_message})
            response.status_code = 400
            response.headers['Content-Type'] = 'application/json'
            print(response)
            return response
    else:
        #crear token
        #guardar token
        token = uuid.uuid1() 
        usuarioConToken = usuarioService.agregarTokenUsuario(usuarioIniciado,token)

        usuarioToken = {
            "id" : usuarioConToken.id,
            "nombre" : usuarioConToken.nombre,
            "contrasenia" : usuarioConToken.contrasenia,
            "gmail" : usuarioConToken.gmail,
            "imagen" : usuarioConToken.imagen,
            "token" : usuarioConToken.token
        }

        return usuarioToken

@app.route('/valoracionUsuario', methods=['POST'])
def agregarValoracionUsuario():
    lugarService = LugarService(getEngine())
    datosLugar = request.get_json()
    idLugar = datosLugar.get('idLugar')  
    valoracion = datosLugar.get('valoracion')

    if idLugar is not None and valoracion is not None:
        lugarService.guardarValoracionUsuario(idLugar, valoracion)
        return jsonify({"idLugar": idLugar, "valoracion": valoracion}), 200
    else:
        return jsonify({"error": "datos incompletos"}), 400

@app.route('/agregarResenia', methods=['POST'])
def agregarReseniaLugar():
    lugarService = LugarService(getEngine())
    datos = request.get_json()
    idLugar = datos.get('idLugar')  
    opinion= datos.get('opinion')  
    usuario = datos.get('idUsuario')

    lugarService.guardarResenia(idLugar,opinion,usuario)

    reseniaAgregada = {
        'resenia': opinion
    }

    return jsonify(reseniaAgregada)

@app.route('/ultimasReseniasRealizadas/<string:idLugar>', methods=['GET'])
def getUltimasResenias(idLugar):
    lugarService = LugarService(getEngine())
    #idLugar = datos.get('idLugar')
    
    resenias = lugarService.getUltimasResenias(idLugar)

    reseniasObtenidas = []
        
    for resenia in resenias:
        resenia_data = {
            'idlugar': resenia[0], 
            'resenia': resenia[1],
            'usuario' :resenia[2],
            'imagen_usuario' :resenia[3]
        }
        reseniasObtenidas.append(resenia_data)

    print("app resenias", reseniasObtenidas)

    return jsonify(reseniasObtenidas)

@app.route('/obtenerOpinionUsuario/<string:idLugar>', methods=['GET'])
def obtenerOpinionUsuario(idLugar):
    lugarService = LugarService(getEngine())
    #idLugar = datos.get('idLugar')
    
    usuarioValoracion = lugarService.obtenerValoracionUsuario(idLugar)

    valoracion ={
        'opinion' : usuarioValoracion.valoracion_usuario
    }

    return valoracion


@app.route('/getLugaresPorActividad/<int:idActividad>/<int:idCiudad>', methods=['GET'])
def getLugaresPorActividad(idActividad,idCiudad):
    actividadService = ActividadesService(getEngine())
    lugaresActividad = actividadService.getLugaresDeActividad(idActividad,idCiudad)

    lugaresJSON = []
    
    for lugarActividad in lugaresActividad:
        lugar = {
            "nombre": lugarActividad[2],
            "id_lugar" : lugarActividad[1]
        }

        lugaresJSON.append(lugar)

    return jsonify(lugaresJSON)

@app.route('/categoriasUsuario/<idUsuario>', methods= ['GET'])
def getCategoriasUsuario(idUsuario):
    categoriaService = CategoriaService(getEngine())
    categoriasObtenidas = []

    categorias = categoriaService.getCategoriasUsuarioConNombre(idUsuario)

    for categoriaActual in categorias:
        categoria = {
            "id":categoriaActual[0],
            "nombre": categoriaActual[1]
        }
        categoriasObtenidas.append(categoria)

    return jsonify(categoriasObtenidas)

