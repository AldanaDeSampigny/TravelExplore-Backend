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

    def calcularTiempotiempoTraslado(self,origenM, destinoM, transporteM):
        with Session(getEngine()) as session:
            if destinoM:
                tiempotraslado = tiempotraslado(
                    origen=str(origenM.latitud) + "," + str(origenM.longitud),
                    destino=str(destinoM.latitud) + "," + str(destinoM.longitud),
                    transporte= transporteM
                )
                #print(tiempotraslado)
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

    #!en revisicion
    # def recomendaciones_IA(self, usuarioID, actividadIds):
    #     recomendadas = self.getActividadesRecomendadas(usuarioID)
    #     listaInicial = [actividadIds[0][0]]
    #     for _ in range(len(actividadIds)):
    #         cerca = self.calculoDeDistancias(1, 1, listaInicial[-1], listaInicial[-2], actividadIds)
    #         listaInicial.append(cerca)
    #     return listaInicial
        # recomendadas = []
        # recomendadas = self.getActividadesRecomendadas(usuarioID)
        # for recomendacion in recomendadas:
        #     print("reco ", recomendacion.id)
        #     recomendacion_id = (recomendacion.id,) if not isinstance(
        #         recomendacion.id, tuple) else recomendacion.id

        #     listaInicial = []
        #     listaInicial.append(actividadIds[0][0])
        #     cerca = self.calculoDeDistancias(
        #         1, 1, actividadIds[0][0], actividadIds[0][0], actividadIds)
        #     listaInicial.append(cerca)
        #     for _ in range(0, len(actividadIds)):
        #         cerca = self.calculoDeDistancias(
        #             1, 1, listaInicial[-1], listaInicial[-2], actividadIds)
        #         listaInicial.append(cerca)

        #     return listaInicial
        
    def calcular_horas_ocupado(self, fecha_actual, horariosOcupados, hora_actual, actividad):
        print("prueba de que llega a calcular_horas ", hora_actual)
        horarios = {
            "hora_cierre_intervalo" : None,
            "hora_actual": None
        }

        if fecha_actual.date().strftime('%Y-%m-%d') in horariosOcupados:
            for horario_ocupado in horariosOcupados[fecha_actual.date().strftime('%Y-%m-%d')]:
                horaInicioOcupado = datetime.strptime(horario_ocupado[0], '%H:%M:%S').time()
                horaFinOcupado = datetime.strptime(horario_ocupado[1], '%H:%M:%S').time()
                if horaInicioOcupado <= hora_actual < horaFinOcupado:
                    horarios.hora_actual = horaFinOcupado
                    break

        minutos_duracion = actividad.duracion.hour * 60 + actividad.duracion.minute
        horarios.hora_cierre_intervalo = hora_actual.replace(hour=(hora_actual.hour + (minutos_duracion // 60)) % 24, minute=(hora_actual.minute + minutos_duracion % 60) % 60)

        return horarios
    
    def traslado(self, transporte, hora_actual, lugares, actividadIds, IDaux):
        with Session(getEngine()) as session:
            agenda_repo = AgendaRepository(session)
            horas = {"hora_actual": None, "tiempoTraslado": None}
            siguiente_actividad = actividadIds[IDaux + 1] if IDaux + 1 < len(actividadIds) else None
            if siguiente_actividad:
                siguiente_actividad_obj = session.query(Actividad).get(siguiente_actividad)
                siguiente_lugar = agenda_repo.buscarLugar(siguiente_actividad_obj.id)

            if lugares[0]:
                horas.tiempoTraslado = self.calcularTiempoTraslado(lugares[0], siguiente_lugar, transporte)
            
            if horas.tiempoTraslado:
                hora_inicio_datetime = datetime.combine(datetime.today(), hora_actual)
                horas.hora_actual = (hora_inicio_datetime + horas.tiempoTraslado).time()

            return horas

    def aceptar_actividad(self, actividad, lugares, actividadIds, fecha_actual, IDaux, transporte, gustos_agregados, hora_actual, hora_cierre_intervalo):
        with Session(getEngine()) as session:
            resultado = {"tiempoTraslado" : None, "actividad" : None}

            #!probablemente borrar
            # if lugares:
            #     horarios = self.lugarHorarios(lugares[0].id)

            #     horarios_filtrados = list(
            #         filter(lambda horario: horario['dia'] == self.dias_semana[fecha_actual.weekday()], horarios))

            #     for horario in horarios_filtrados:
            #         hora_inicio = datetime.strptime(horario['horaInicio'], "%H:%M:%S").time()
            #         hora_fin = datetime.strptime(horario['horaFin'], "%H:%M:%S").time() 
                    
            #         if hora_inicio <= hora_actual < hora_fin:
            #             print("inicio ", hora_inicio, " fin ", hora_fin)
            
            if actividad.horainicio <= hora_actual < actividad.horafin:
                horas = self.traslado(transporte, hora_actual, lugares, actividadIds, IDaux)

                if actividad.id not in gustos_agregados:
                    resultado.actividad = {
                        'dia': fecha_actual,
                        'hora_inicio': horas.hora_actual,
                        'hora_fin': hora_cierre_intervalo,
                        'actividad': actividad,
                        'lugar': lugares[0].nombre if lugares else "null",
                        'lugares': lugares
                    }

            return resultado
        
    def obtener_horarios_dia(self, fecha_actual, horariosElegidos, horaInicio, horaFin):
        if fecha_actual.date().strftime('%Y-%m-%d') in horariosElegidos:
            hora_actual = datetime.strptime(horariosElegidos[fecha_actual.date().strftime('%Y-%m-%d')][0], '%H:%M:%S').time()
            horario_fin = datetime.strptime(horariosElegidos[fecha_actual.date().strftime('%Y-%m-%d')][1], '%H:%M:%S').time()
        else:
            hora_actual = datetime.strptime(horaInicio, '%H:%M:%S').time()
            horario_fin = datetime.strptime(horaFin, '%H:%M:%S').time()
        return hora_actual, horario_fin

    def generarAgendaDiaria(self, usuarioID, destinoID, horariosElegidos, horariosOcupados,fechaDesde, fechaHasta, horaInicio, horaFin, transporte):
        with Session(getEngine()) as session:
            agenda_repo = AgendaRepository(session)
            agenda = []
            gustos_agregados = set()

            fecha_actual = datetime.strptime(fechaDesde, '%Y-%m-%d')
            fecha_hasta = datetime.strptime(fechaHasta, '%Y-%m-%d')
            actividadIds = agenda_repo.buscarActividad(usuarioID, destinoID)
            
            #parte de la IA
            #llamar aca

            #actividadIds = listaInicial.copy()
            #actividadIds = this.recomendacionesID.copy()
            
            while fecha_actual <= fecha_hasta:
                hora_actual, horario_fin = self.obtener_horarios_dia(fecha_actual, horariosElegidos, horaInicio, horaFin)

                actividadIds_set = set(np.array(actividadIds).flatten())

                if gustos_agregados == actividadIds_set:
                    gustos_agregados.clear()

                while hora_actual < horario_fin:
                    for IDaux, actividad_id in enumerate(actividadIds):
                        actividad = session.query(Actividad).get(actividad_id)

                        lugares = agenda_repo.buscarLugares(actividad.id, destinoID)

                        horarios = self.calcular_horas_ocupado(fecha_actual, horariosOcupados, hora_actual, actividad)

                        resultado = self.aceptar_actividad(actividad, lugares, actividadIds, fecha_actual, IDaux, transporte, gustos_agregados, horarios.hora_actual, horarios.hora_cierre_intervalo)
                        
                        hora_actual = resultado.hora_actual
                        
                        agenda.append(resultado.actividad)
                        gustos_agregados.add(resultado.actividad.id)
                            
                    if datetime.strptime('00:00:00', '%H:%M:%S').time() <= hora_actual <= datetime.strptime('04:00:00', '%H:%M:%S').time():
                        break

                    hora_inicio_datetime = datetime.combine(datetime.now().date(), horarios.hora_cierre_intervalo)
                    if resultado.tiempoTraslado:
                        hora_inicio_datetime += resultado.tiempoTraslado
                    hora_actual = hora_inicio_datetime.time() 
                
                fecha_actual += timedelta(days=1)

        return agenda
