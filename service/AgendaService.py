import math
from turtle import update
import json

import numpy as np
from sqlalchemy import Row

from ..PruebaIA import PruebaIA

from ..models.Lugar import Lugar

from ..repository.UsuarioRepository import UsuarioRepository

from ..models.AgendaViaje import AgendaViaje

from ..models.ActividadAgenda import ActividadAgenda
from sqlalchemy.sql.expression import func
from ..consultas import obtenerDirecciones

from ..models.Actividad import Actividad
from ..models.Viaje import Viaje
from ..models.Itinerario import Itinerario
from ..models.AgendaDiaria import AgendaDiaria
from ..repository.AgendaRepository import AgendaRepository
from ..bd.conexion import getEngine
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

class AgendaService:
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

    def calcularTiempoTraslado(self,origenM, destinoM, transporteM):
        with Session(getEngine()) as session:
            if destinoM:
                direccion = obtenerDirecciones(
                    origen=str(origenM.latitud) + "," + str(origenM.longitud),
                    destino=str(destinoM.latitud) + "," + str(destinoM.longitud),
                    transporte= transporteM
                )
                #print(direccion)
            else:
                direccion = None

            print(direccion)
            return direccion
        
    def getAgenda(self,usuarioID,agendaID):
        with Session(getEngine()) as session:
            agenda = UsuarioRepository(session)

            agendaUsuario = agenda.getAgendaUsuario(usuarioID,agendaID)

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

    def calculoDeDistancias(self, usuarioID, destinoID, ultimo, anteultimo ,actividades):
        with Session(getEngine()) as session:
            agenda_repo = AgendaRepository(session)
            distancias = []
            # print("ultimo", ultimo)
            # print("anteultimo", anteultimo)
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
            #print(distancias_ordenadas)
            cerca = distancias_ordenadas[0]["actividad"]
            #print(cerca)
            
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
            recomendacionesIA = recomendaciones.cargadoDeIA(usuarioID)
            
            return recomendacionesIA

    def generarAgendaDiaria(self, usuarioID, destinoID, horariosElegidos, horariosOcupados,fechaDesde, fechaHasta, horaInicio, horaFin, transporte):
        with Session(getEngine()) as session:
            agenda_repo = AgendaRepository(session)
            agenda = []
            direccion = None

            fecha_actual = datetime.strptime(fechaDesde, '%Y-%m-%d')
            fecha_hasta = datetime.strptime(fechaHasta, '%Y-%m-%d')
            delta_dias = timedelta(days=1)

            gustos_agregados = set()
            actividadIds = agenda_repo.buscarActividad(usuarioID, destinoID)
            
            recomendadas = []
            recomendadas = self.getActividadesRecomendadas(usuarioID)
            for recomendacion in recomendadas:
                actividadIds.append(recomendacion.id)

            listaInicial = []
            listaInicial.append(actividadIds[0][0])
            cerca = self.calculoDeDistancias(
                1, 1, actividadIds[0][0], actividadIds[0][0], actividadIds)
            listaInicial.append(cerca)
            for i in range(0, len(actividadIds)):
                cerca = self.calculoDeDistancias(
                    1, 1, listaInicial[-1], listaInicial[-2], actividadIds)
                listaInicial.append(cerca)

            actividadIds = listaInicial.copy()

            while fecha_actual <= fecha_hasta:

                if fecha_actual.date().strftime('%Y-%m-%d') in horariosElegidos:
                    hora_actual = datetime.strptime(horariosElegidos[fecha_actual.date().strftime('%Y-%m-%d')][0], '%H:%M:%S').time()
                    horario_fin = datetime.strptime(
                        horariosElegidos[fecha_actual.date().strftime('%Y-%m-%d')][1], '%H:%M:%S').time()
                else:
                    hora_actual = datetime.strptime(horaInicio, '%H:%M:%S').time() 
                    horario_fin = datetime.strptime(horaFin, '%H:%M:%S').time()

                actividadIds_set = set(np.array(actividadIds).flatten())

                if gustos_agregados == actividadIds_set:
                    gustos_agregados.clear()

                while hora_actual < horario_fin:
                    for idx, m_id in enumerate(actividadIds):

                        m = session.query(Actividad).get(m_id)
                        print("actividad ", m.nombre)
                        lugar = agenda_repo.buscarLugar(m.id)

                        if fecha_actual.date().strftime('%Y-%m-%d') in horariosOcupados:
                            for horario_ocupado in horariosOcupados[fecha_actual.date().strftime('%Y-%m-%d')]:
                                horaInicioOcupado = datetime.strptime(horario_ocupado[0], '%H:%M:%S').time()
                                horaFinOcupado = datetime.strptime(horario_ocupado[1], '%H:%M:%S').time()
                                if horaInicioOcupado <= hora_actual < horaFinOcupado:
                                    hora_actual = horaFinOcupado
                                    break
                            
                        minutos_duracion = m.duracion.hour * 60 + m.duracion.minute
                        hora_cierre_intervalo = hora_actual.replace(hour=(hora_actual.hour + (minutos_duracion // 60)) % 24, minute=(hora_actual.minute + minutos_duracion % 60) % 60)

                        if lugar.horaapertura <= hora_actual < lugar.horacierre:
                            print("ac inio ", m.horainicio)
                            print("ac  ", hora_actual)
                            print("ac fin ", m.horafin)
                            if m.horainicio <= hora_actual < m.horafin:
                                print("entro ", hora_actual)
                                siguiente_actividad = actividadIds[idx + 1] if idx + 1 < len(actividadIds) else None
                                if siguiente_actividad:
                                    siguiente_actividad_obj = session.query(Actividad).get(siguiente_actividad)
                                    siguiente_lugar = agenda_repo.buscarLugar(siguiente_actividad_obj.id)

                                direccion = self.calcularTiempoTraslado(lugar, siguiente_lugar, transporte)
                                if direccion:
                                    hora_inicio_datetime = datetime.combine(datetime.today(), hora_actual)
                                    hora_actual = (hora_inicio_datetime + direccion).time()
            
                                if m.id not in gustos_agregados:
                                    actividad = {
                                        'dia': fecha_actual,
                                        'hora_inicio': hora_actual,
                                        'hora_fin': hora_cierre_intervalo,
                                        'actividad': m,
                                        'lugar': lugar.nombre
                                    }
                                    agenda.append(actividad)
                                    gustos_agregados.add(m.id)
                                    break
                            
                    if datetime.strptime('00:00:00', '%H:%M:%S').time() <= hora_actual <= datetime.strptime('04:00:00', '%H:%M:%S').time():
                        break

                    hora_inicio_datetime = datetime.combine(datetime.now().date(), hora_cierre_intervalo)
                    if direccion:
                        hora_inicio_datetime += direccion
                    hora_actual = hora_inicio_datetime.time() 
                
                fecha_actual += delta_dias

        return agenda
