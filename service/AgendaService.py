from turtle import update
import json

import numpy as np

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
    """  horas = {datetime.strptime('08:00:00', '%H:%M:%S').time(): datetime.strptime('10:00:00', '%H:%M:%S').time(),
                        datetime.strptime('12:00:00', '%H:%M:%S').time(): datetime.strptime('14:00:00', '%H:%M:%S').time(),
                        datetime.strptime('18:00:00', '%H:%M:%S').time(): datetime.strptime('19:00:00', '%H:%M:%S').time(),
                        datetime.strptime('21:00:00', '%H:%M:%S').time(): datetime.strptime('23:00:00', '%H:%M:%S').time()}
        """
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
                diax = timedelta(days=1)
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
                        actividadAgendaNueva.id_agenda = nuevaAgendaDiaria.id
                        session.add(actividadAgendaNueva)
                        session.commit()

            except Exception as e:
                # En caso de error, realiza un rollback
                session.rollback()
                raise e

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
        
    def getAgenda(self,usuario):
        with Session(getEngine()) as session:
            agenda = UsuarioRepository(session)

            agendaUsuario = agenda.getAgendaUsuario(usuario)

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

        return agendasDestino;

#generador de agenda diaria con dias ocupados, y horarios especificos
    def generarAgendaDiaria(self, usuarioID, destinoID, horariosElegidos, horariosOcupados,fechaDesde, fechaHasta, horaInicio, horaFin, transporte):
        with Session(getEngine()) as session:
            agenda_repo = AgendaRepository(session)
            agenda = []

            fecha_actual = datetime.strptime(fechaDesde, '%Y-%m-%d')
            fecha_hasta = datetime.strptime(fechaHasta, '%Y-%m-%d')
            delta_dias = timedelta(days=1)

            gustos_agregados = set()
            actividadIds = agenda_repo.buscarActividad(usuarioID, destinoID)
            while fecha_actual <= fecha_hasta:

                if fecha_actual.date().strftime('%Y-%m-%d') in horariosElegidos:
                    hora_actual = datetime.strptime(horariosElegidos[fecha_actual.date().strftime('%Y-%m-%d')][0], '%H:%M:%S').time()
                    horario_fin = datetime.strptime(horariosElegidos[fecha_actual.date().strftime('%Y-%m-%d')][1], '%H:%M:%S').time()
                else:
                    hora_actual = datetime.strptime(horaInicio, '%H:%M:%S').time() 
                    horario_fin = datetime.strptime(horaFin, '%H:%M:%S').time()

                actividadIds_set = set(np.array(actividadIds).flatten())

                if gustos_agregados == actividadIds_set:
                    gustos_agregados.clear()

                while hora_actual < horario_fin:
                    for idx, m_id in enumerate(actividadIds):
                        m = session.query(Actividad).get(m_id[0])
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

                        
                        #podria traer una query que traiga un lugar de tipo restaurante y los meta aca
                        # if hora_actual in self.horas:
                        #     actividad = agenda_repo.buscarActividadRestaurant(usuarioID, destinoID)
                        #     lugarA = agenda_repo.buscarLugar(actividad.id)
                        #     if lugarA.horaApertura < hora_actual < lugarA.horaCierre:
                        #         if actividad.id not in gustos_agregados:
                        #             actividades = {
                        #                 'dia': fecha_actual,
                        #                 'hora_inicio': hora_actual,
                        #                 'hora_fin': hora_cierre_intervalo,
                        #                 'actividad': actividad,
                        #                 'lugar': lugar.nombre
                        #             }
                        #             agenda.append(actividades)
                        #             gustos_agregados.add(actividad.id)
                        #             break
                        
                        if lugar.horaApertura <= hora_actual < lugar.horaCierre:

                            siguiente_actividad = actividadIds[idx + 1] if idx + 1 < len(actividadIds) else None
                            if siguiente_actividad:
                                siguiente_actividad_obj = session.query(Actividad).get(siguiente_actividad[0])
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

                    hora_inicio_datetime = datetime.combine(datetime.now().date(), hora_cierre_intervalo)  # Crear un objeto datetime
                    hora_inicio_datetime += direccion  # Sumar la dirección al objeto datetime
                    hora_actual = hora_inicio_datetime.time() 
                
                fecha_actual += delta_dias
                #print(fecha_actual)

            #session.commit()
            #session.close()

        # self.saveAgenda(usuarioID,destinoID,fechaDesde,fechaHasta,horaInicio,horaFin,fechaHasta,agenda)
        return agenda