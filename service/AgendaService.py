import math
from turtle import update
import json

from ..repository.ActividadRepository import ActividadRepository
from ..repository.LugarRepository import LugarRepository

import numpy as np
from sqlalchemy import Row

from ..PruebaIA import PruebaIA

from ..models.Lugar import Lugar

from ..repository.UsuarioRepository import UsuarioRepository
from ast import literal_eval
from ..models.AgendaViaje import AgendaViaje

from ..models.ActividadAgenda import ActividadAgenda
from sqlalchemy.sql.expression import func
from ..consultas import obtenerDirecciones

from ..models.Actividad import Actividad
from ..models.ActividadLugar import ActividadLugar
from ..models.Viaje import Viaje
from ..models.Itinerario import Itinerario
from ..models.AgendaDiaria import AgendaDiaria
from ..repository.AgendaRepository import AgendaRepository
from ..bd.conexion import getEngine
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

class AgendaService:

    dias_semana = ["Monday", "Tuesday", "Wednesday",
                    "Thursday", "Friday", "Saturday", "Sunday"]
    
    def __init__(self, db_session):
        self.db_session = db_session

    def saveAgenda(self, idUsuario, idCiudad, fechaDesde, fechaHasta, horaInicio, horaFin, agenda):
        with Session(getEngine()) as session:
    
            nuevoViaje = Viaje()
            nuevoViaje.id_usuario = idUsuario
            nuevoViaje.fechaDesde = fechaDesde
            nuevoViaje.fechaHasta = fechaHasta

            try:
                session.add(nuevoViaje)
                session.commit()

                agendaViajeNueva = AgendaViaje()
                session.add(agendaViajeNueva)
                session.commit()

                nuevoItinerario = Itinerario()
                nuevoItinerario.id_ciudad = idCiudad
                nuevoItinerario.fechaDesde = fechaDesde
                nuevoItinerario.fechaHasta = fechaHasta
                nuevoItinerario.id_viaje = nuevoViaje.id
                session.add(nuevoItinerario)
                session.commit()

                fecha = datetime.strptime(fechaDesde, "%Y-%m-%d")
                for agendaDiaria in agenda:
                    nuevaAgendaDiaria = AgendaDiaria()
                    nuevaAgendaDiaria.horaInicio = horaInicio
                    print("horaInicio", horaInicio)
                    nuevaAgendaDiaria.horaFin = horaFin
                    print("horaFin", horaFin)
                    nuevaAgendaDiaria.dia = fecha.strftime("%Y-%m-%d")
                    nuevaAgendaDiaria.itinerario_id = nuevoItinerario.id
                    nuevaAgendaDiaria.id_agenda_viaje = agendaViajeNueva.id
                    fecha += timedelta(days=1)

                    session.add(nuevaAgendaDiaria)
                    session.commit()

                    for actividadAgenda in agendaDiaria.get('actividades', []):
                        actividadAgendaNueva = ActividadAgenda()
                        actividadAgendaNueva.id_actividad = actividadAgenda.get('id', None)
                        actividadAgendaNueva.id_lugar = actividadAgenda.get('lugar', None)
                        actividadAgendaNueva.horadesde = actividadAgenda.get('hora_inicio', None)
                        actividadAgendaNueva.horahasta = actividadAgenda.get('hora_fin', None)
                        actividadAgendaNueva.id_agenda = nuevaAgendaDiaria.id
                        session.add(actividadAgendaNueva)
                        session.commit()

            except Exception as e:
                # En caso de error, realiza un rollback
                session.rollback()
                raise e
            
            return agendaViajeNueva.id

    def modificar_agenda_diaria(self, agendadiaria):
        with Session(getEngine()) as session:
            repository = AgendaRepository(session)

            # Recuperar la actividad existente
            agenda = repository.getActividadAgendaDiaria(agendadiaria['id'], agendadiaria['actividad']['id'])

            if agenda:
                # Actualizar los campos
                agenda.horadesde = agendadiaria['horaInicio']
                agenda.horahasta = agendadiaria['horaFin']
                print("ID LUGAR: ", agendadiaria['lugar']['id_lugar'])
                agenda.id_lugar = agendadiaria['lugar']['id_lugar']

                print("AGENDA ACTUALIZADA: ", agenda)
                session.add(agenda)
                session.commit()
            else:
                print(f"No se encontró la actividad con ID {agendadiaria['id']} y actividad ID {agendadiaria['actividad']['id']}")

    def calcular_tiempo_traslado(self,origenM, destinoM, transporteM):
        if destinoM:
            tiempotraslado = obtenerDirecciones(
                origen=str(origenM.latitud) + "," + str(origenM.longitud),
                destino=str(destinoM.latitud) + "," + str(destinoM.longitud),
                transporte= transporteM
            )
        else:
            tiempotraslado = None

        print(tiempotraslado)
        return tiempotraslado
        
    def getAgenda(self,usuarioID,agendaID):
        with Session(getEngine()) as session:
            agenda = UsuarioRepository(session)

            agendaUsuario = agenda.getAgendaUsuario(usuarioID,agendaID)

            print("agenda usuario ", agendaUsuario)
        return agendaUsuario;
        
    def obtenerAgendasUsuario(self,usuarioID):
        with Session(getEngine()) as session:
            agenda = UsuarioRepository(session)

            agendasUsuario = agenda.obtenerAgendasUsuario(usuarioID)

        return agendasUsuario;

    def obtenerAgendasUsuarioConDestino(self,usuarioID):
        with Session(getEngine()) as session:
            agenda = UsuarioRepository(session)

            agendasDestino = agenda.todasLasAgendasUsuario(usuarioID).all()

        return agendasDestino
    
    def obtenerActividadAgenda(self, idActividad, idAgenda):
        with Session(getEngine()) as session:
            agenda = AgendaRepository(session)

            actividadAgenda = agenda.getActividadAgenda(idActividad, idAgenda)

        return actividadAgenda

    def obtenerLugaresDeActividades(self,idCiudad,idActividad):
        with Session(getEngine()) as session:
            actividadRepository = ActividadRepository(session)

            lugaresDeActividad = actividadRepository.getLugaresDeActividad(idCiudad, idActividad)

            return lugaresDeActividad

    def obtenerAgendaDiaria(self, idAgenda):
        with Session(getEngine()) as session:
            agendaRepository = AgendaRepository(session)

            actividadesAgenda = agendaRepository.getAgendaDiaria(idAgenda)

            return actividadesAgenda

    def haversine_distance(self, lat1, lon1, lat2, lon2):
    # Radio de la Tierra en kilómetros
        R = 6371.0

        # Convertir las latitudes y longitudes de grados a radianes
        lat1 = math.radians(lat1)
        lon1 = math.radians(lon1)
        lat2 = math.radians(lat2)
        lon2 = math.radians(lon2)

        # Diferencia en latitudes y longitudes
        delta_lat = lat2 - lat1
        delta_lon = lon2 - lon1

        # Fórmula Haversine
        a = math.sin(delta_lat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c

        return distance
    
    # Función para convertir grados a radianes
    def to_rad(self, x):
        return x * math.pi / 180

    def distanciaEntreCoords(self, latLugar, longLugar, latEstadia, longEstadia):
        R = 6371  # radio de la Tierra en km
        dLat = self.to_rad(latLugar - latEstadia)
        dLon = self.to_rad(longEstadia - longLugar)
        lat1_rad = self.to_rad(latLugar)
        lat2_rad = self.to_rad(latEstadia)

        a = math.sin(dLat / 2) * math.sin(dLat / 2) + \
            math.cos(lat1_rad) * math.cos(lat2_rad) * \
            math.sin(dLon / 2) * math.sin(dLon / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c

        return distance



    # Calcular la distancia entre las coordenadas
    # distance = calculate_distance(coord1[0], coord1[1], coord2[0], coord2[1])
    # print(f"La distancia entre Nueva York y Los Ángeles es de {distance:.2f} km.")

    def calculoDeDistancias(self, usuarioID, destinoID, ultimo, anteultimo ,actividades):
        with Session(getEngine()) as session:
            agenda_repo = AgendaRepository(session)
            distancias = []
            ultimoLugar = agenda_repo.buscarLugar(ultimo)
            #anteultimo = agenda_repo.buscarLugar(anteultimo[0])

            actividades = agenda_repo.buscarActividad(usuarioID, destinoID)

            for uno in range(len(actividades)):
                if ultimo != actividades[uno].id and anteultimo != actividades[uno].id:
                    # print("uno ",uno)
                    # print("ultimo ", ultimo)
                    # print("anteultimo ", anteultimo)
                    lugar2 = agenda_repo.buscarLugar(actividades[uno].id)
                    distancia = self.haversine_distance(
                        ultimoLugar.latitud, ultimoLugar.longitud, lugar2.latitud, lugar2.longitud)
                    distancias.append({
                        "actividad": actividades[uno].id,
                        "lugar": lugar2,
                        "distancia": distancia
                    })
                    
            distancias_ordenadas = sorted(distancias, key=lambda x: x["distancia"])
            print("distancias ",distancias_ordenadas)
            cerca = distancias_ordenadas[0]["actividad"]
            
        return cerca 
    
    def eliminarActividadAgeenda(self, idActividad, idAgendaViaje):
        with Session(getEngine()) as session:
            agendaRepo = AgendaRepository(session)
            agendasDiarias = agendaRepo.getAgendasDeViaje(idAgendaViaje)
            for agenda in agendasDiarias:
                agendaRepo.deleteActividadesDeAgenda(idActividad, agenda.id)

    def getActividadesRecomendadas(self, usuarioID):
        with Session(getEngine()) as session:
            recomendaciones = PruebaIA(session)
            print("recomendaciones", recomendaciones.cargadoDeIA(usuarioID))
            recomendacionesIA = recomendaciones.cargadoDeIA(usuarioID)

            
            return recomendacionesIA
        
    def lugarHorarios(self, idlugar):
        with Session(getEngine()) as session:
            lugarRepo = LugarRepository(session)
            horariosDelLugar = lugarRepo.getLugarHorario(idlugar)
            horarios = []

            for row in horariosDelLugar:
                horario = {
                    "dia": row[0],
                    "horaInicio": row[1].strftime("%H:%M:%S") if row[1] else None,
                    "horaFin": row[2].strftime("%H:%M:%S") if row[2] else None,
                }
                horarios.append(horario)

            return horarios

    def recomendaciones_IA(self, usuarioID):
        recomendaciones = []
        recomendadas = []
        recomendadas = self.getActividadesRecomendadas(usuarioID)
        for recomendacion in recomendadas:
            print("reco ", recomendacion.id)
            aux = (recomendacion.id,) 
            recomendaciones.append(aux)

        print("lista",recomendaciones)
        return recomendaciones
        
    def calcular_horas_ocupado(self, fecha_actual, horariosOcupados, hora_actual, actividad):
        horarios = {
            "hora_cierre_intervalo" : None,
            "hora_actual": hora_actual}

        if fecha_actual.date().strftime('%Y-%m-%d') in horariosOcupados:
            for horario_ocupado in horariosOcupados[fecha_actual.date().strftime('%Y-%m-%d')]:
                horaInicioOcupado = datetime.strptime(horario_ocupado[0], '%H:%M:%S').time()
                horaFinOcupado = datetime.strptime(horario_ocupado[1], '%H:%M:%S').time()
                if horaInicioOcupado <= hora_actual < horaFinOcupado:
                    horarios['hora_actual'] = horaFinOcupado
                    break

        minutos_duracion = actividad.duracion.hour * 60 + actividad.duracion.minute
        horarios['hora_cierre_intervalo'] = horarios['hora_actual'].replace(
            hour=(hora_actual.hour + (minutos_duracion // 60)) % 24, 
            minute=(hora_actual.minute + minutos_duracion % 60) % 60)

        return horarios
    
    def traslado(self, transporte, hora_actual, lugar, actividadIds, IDaux):
        with Session(getEngine()) as session:
            horas = {"hora_actual": None, "tiempoTraslado": None}
            siguiente_actividad_id = actividadIds[IDaux + 1][0] if IDaux + 1 < len(actividadIds) else None

            siguiente_lugar = None
            if siguiente_actividad_id:
                siguiente_lugar = session.query(Lugar).join(
                    ActividadLugar, ActividadLugar.id_lugar == Lugar.id
                ).filter(ActividadLugar.id_actividad == siguiente_actividad_id
                ).first()
        
            #?siguiente_lugar es llamado abajo pero esta comentado MOMENTANEAMENTE
            if lugar:
                horas['tiempoTraslado'] = timedelta(minutes=5)#self.calcularTiempoTraslado(lugares[0], siguiente_lugar, transporte)
            else:
                horas['tiempoTraslado'] = timedelta(minutes = 5)
                
            if horas['tiempoTraslado']:
                hora_inicio_datetime = datetime.combine(datetime.today(), hora_actual)
                print("traslado horainiciodatetime ", hora_inicio_datetime)
                horas['hora_actual'] = (hora_inicio_datetime + horas['tiempoTraslado']).time()

            return horas

    def aceptar_actividad(self, actividad, lugar, lugares, actividadIds, fecha_actual, IDaux, transporte, gustos_agregados, hora_actual, hora_cierre_intervalo):
        with Session(getEngine()) as session:
            resultado = {'tiempoTraslado' : None, 'actividad' : None, 'hora_actual': hora_actual}
 
            
            if actividad.horainicio <= hora_actual < actividad.horafin:
                resultado['hora_actual'] = self.traslado(transporte, hora_actual, lugar, actividadIds, IDaux)

                if actividad.id not in gustos_agregados:
                    resultado['actividad'] = {
                        'id': actividad.id,
                        'dia': fecha_actual,
                        'hora_inicio': resultado['hora_actual']['hora_actual'],
                        'hora_fin': hora_cierre_intervalo,
                        'actividad': actividad,
                        'lugar': lugar.id if lugar else None,
                        'lugares': lugares if lugares else []
                    }


                    print("Actividad aceptada: ", resultado['actividad']['id'])
                    print("hora actual: ", resultado['hora_actual']['hora_actual'])

            return resultado
        
    def obtener_horarios_dia(self, fecha_actual, horariosElegidos, horaInicio, horaFin):
        if fecha_actual.date().strftime('%Y-%m-%d') in horariosElegidos:
            hora_actual = datetime.strptime(horariosElegidos[fecha_actual.date().strftime('%Y-%m-%d')][0], '%H:%M:%S').time()
            horario_fin = datetime.strptime(horariosElegidos[fecha_actual.date().strftime('%Y-%m-%d')][1], '%H:%M:%S').time()
        else:
            hora_actual = datetime.strptime(horaInicio, '%H:%M:%S').time()
            horario_fin = datetime.strptime(horaFin, '%H:%M:%S').time()
        return hora_actual, horario_fin

    def obtenerLugar(self, lugares, latitudHospedaje, longitudHospedaje):
        with Session(getEngine()) as session:
            matrizLugar = []
            valoracion_minima = 0
            distancia_maxima = 8000.0

            for lugar in lugares:
                calculo = self.distanciaEntreCoords(lugar.latitud, lugar.longitud, latitudHospedaje, longitudHospedaje)
                matrizLugar.append([lugar.id, lugar.valoracion, calculo])
            
            
            lugar_optimo = None
            for lugar in matrizLugar:
                id_lugar, valoracion, distancia = lugar
                if valoracion >= valoracion_minima and distancia <= distancia_maxima:
                    valoracion_minima = valoracion
                    distancia_maxima = distancia
                    lugar_optimo = id_lugar

            lugar_seleccionado = session.query(Lugar).get(lugar_optimo)
            return lugar_seleccionado

    def generarAgendaDiaria(self, ubicacion, usuarioID, destinoID, horariosElegidos, horariosOcupados,fechaDesde, fechaHasta, horaInicio, horaFin, transporte):
        with Session(getEngine()) as session:
            agenda_repo = AgendaRepository(session)
            agenda = []
            gustos_agregados = set()

            fecha_actual = datetime.strptime(fechaDesde, '%Y-%m-%d')
            fecha_hasta = datetime.strptime(fechaHasta, '%Y-%m-%d')
            actividadIds = agenda_repo.buscarActividad(usuarioID, destinoID)

            print("actividad",actividadIds)
            actividadIds.extend(self.recomendaciones_IA(usuarioID)) 
            
            while fecha_actual <= fecha_hasta:
                print("--- Fecha ---", fecha_actual)
                hora_actual, horario_fin = self.obtener_horarios_dia(fecha_actual, horariosElegidos, horaInicio, horaFin)
                print("hora actual 1", hora_actual)
                actividadIds_set = set(np.array(actividadIds).flatten())

                if gustos_agregados == actividadIds_set:
                    gustos_agregados.clear()

                while hora_actual < horario_fin:
                    print("segundo whilewhile hora actual", hora_actual)
                    for IDaux, actividad_id in enumerate(actividadIds):
                        actividad = session.query(Actividad).get(actividad_id)

                        lugares = agenda_repo.buscarLugares(actividad.id, destinoID)
                        
                        lugar = self.obtenerLugar(lugares, ubicacion.latitude, ubicacion.longitude)
                        

                        horarios = self.calcular_horas_ocupado(fecha_actual, horariosOcupados, hora_actual, actividad)

                        resultado = self.aceptar_actividad(actividad, lugar, lugares, actividadIds, fecha_actual, IDaux, transporte, gustos_agregados, horarios['hora_actual'], horarios['hora_cierre_intervalo'])
                        
                        if resultado['actividad']:
                            hora_actual = resultado['hora_actual']['hora_actual']
                            print("1)hora actual: ", hora_actual)

                            agenda.append(resultado['actividad'])
                            gustos_agregados.add(resultado['actividad']['id'])
                            
                    if datetime.strptime('00:00:00', '%H:%M:%S').time() <= hora_actual <= datetime.strptime('04:00:00', '%H:%M:%S').time():
                        break

                    hora_inicio_datetime = datetime.combine(datetime.now().date(), horarios['hora_cierre_intervalo'])
                    if resultado['tiempoTraslado']:
                        hora_inicio_datetime += resultado['tiempoTraslado']
                    hora_actual = hora_inicio_datetime.time() 
                
                fecha_actual += timedelta(days=1)

        return agenda

