from turtle import update

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
    horas = {datetime.strptime('08:00:00', '%H:%M:%S').time(): datetime.strptime('10:00:00', '%H:%M:%S').time(),
                    datetime.strptime('12:00:00', '%H:%M:%S').time(): datetime.strptime('14:00:00', '%H:%M:%S').time(),
                    datetime.strptime('18:00:00', '%H:%M:%S').time(): datetime.strptime('19:00:00', '%H:%M:%S').time(),
                    datetime.strptime('21:00:00', '%H:%M:%S').time(): datetime.strptime('23:00:00', '%H:%M:%S').time()}
    
    def __init__(self, db_session):
        self.db_session = db_session

    def saveAgenda(self, idUsuario,idCiudad,fechaDesde,fechaHasta, horaInicio, horaFin, dia,agenda):
        with Session(getEngine()) as session:

            nuevoViaje =  Viaje()
            nuevoViaje.id_usuario = idUsuario
            nuevoViaje.fechaDesde = fechaDesde
            nuevoViaje.fechaHasta = fechaHasta
            
            try:
                for actividadProgramada in agenda:
                    actividad = actividadProgramada['actividad']
                    #print("Actividad" + str(actividad.to_dict()))
                    actividad.id_agenda_diaria = 22
                    session.commit()

                session.add(nuevoViaje)
                session.commit()

                nuevoItinerario = Itinerario()
                nuevoItinerario.id_ciudad= idCiudad
                nuevoItinerario.fechaDesde = fechaDesde
                nuevoItinerario.fechaHasta = fechaHasta
                nuevoItinerario.id_viaje = nuevoViaje.id
                session.add(nuevoItinerario)
                session.commit()

                nuevaAgendaDiaria = AgendaDiaria()
                nuevaAgendaDiaria.horaInicio = horaInicio 
                nuevaAgendaDiaria.horaFin = horaFin
                nuevaAgendaDiaria.dia = dia
                nuevaAgendaDiaria.itinerario_id = nuevoItinerario.id

                session.add(nuevaAgendaDiaria)
                session.commit()
                #session.refresh(nuevaAgendaDiaria)
            except Exception as e:
                # En caso de error, realiza un rollback
                session.rollback()
                raise e
            
    def calcularTiempoTraslado(self,origenM, destinoM, transporteM):
        with Session(getEngine()) as session:
            #siguiente_actividad = meGustas_ids[idx + 1] if idx + 1 < len(meGustas_ids) else None
            if destinoM:
                direccion = obtenerDirecciones(
                    origen=str(origenM.latitud) + "," + str(origenM.longitud),
                    destino=str(destinoM.latitud) + "," + str(destinoM.longitud),
                    transporte= transporteM
                )
                #print(direccion)
            else:
                direccion = None
            return direccion


    """
        Retorna un json de agenda 
    """
#     def generar_agenda(self, usuarioID, viajeID, fechaDesde, fechaHasta, horaInicio, horaFin):
#         with Session(getEngine()) as session:
#             agenda_repo = AgendaRepository(session)
#             agenda = []

#             hora_inicio = datetime.strptime(horaInicio, '%H:%M:%S').time() 
#             hora_cierre_intervalo = datetime.strptime('00:00:00', '%H:%M:%S').time() 
#             inicioNumerico = hora_inicio.hour * 60 + hora_inicio.minute 
#             finNumerico = datetime.strptime(horaFin, '%H:%M:%S').time().hour * 60 + datetime.strptime(horaFin, '%H:%M:%S').time().minute

#             fecha_actual = datetime.strptime(fechaDesde, '%Y-%m-%d')
#             fecha_hasta = datetime.strptime(fechaHasta, '%Y-%m-%d')
#             delta_dias = timedelta(days=1)

#             while fecha_actual <= fecha_hasta:
#                 meGustas_ids = agenda_repo.buscarActividad(usuarioID, viajeID)
#                 hora_inicio = datetime.strptime(horaInicio, '%H:%M:%S').time() 
#                 inicioNumerico = hora_inicio.hour * 60 + hora_inicio.minute 
#                 gustos_agregados = set()
#                 while inicioNumerico < finNumerico:
#                     for idx, m_id in enumerate(meGustas_ids):

#                         m = session.query(Actividad).get(m_id[0])
#                         lugar = agenda_repo.buscarLugar(m.id)

#                         minutos_duracion = m.duracion.hour * 60 + m.duracion.minute
#                         hora_cierre_intervalo = hora_inicio.replace(hour=(hora_inicio.hour + (minutos_duracion // 60)) % 24, minute=(hora_inicio.minute + minutos_duracion % 60) % 60)

#                         siguiente_actividad = meGustas_ids[idx + 1] if idx + 1 < len(meGustas_ids) else None
#                         if siguiente_actividad:
#                             siguiente_actividad_obj = session.query(Actividad).get(siguiente_actividad[0])
#                             siguiente_lugar = agenda_repo.buscarLugar(siguiente_actividad_obj.id)

#                         direccion = self.calcularTiempoTraslado(lugar, siguiente_lugar, 'driving')
#                         if direccion:
#                             hora_inicio_datetime = datetime.combine(datetime.today(), hora_inicio)
#                             hora_inicio = (hora_inicio_datetime + direccion).time()

#                         #PROBLEMA, NO SE METE EN ESTE IF
#                         #podria traer una query que traiga un lugar de tipo restaurante y los meta aca
#                         if lugar.tipo == 'restaurant' and hora_inicio in self.horas and lugar.horaApertura <= hora_inicio < lugar.horaCierre:
#                             if m.id not in gustos_agregados:
#                                 actividad = {
#                                 'dia': fecha_actual,
#                                 'hora_inicio': hora_inicio,
#                                 'hora_fin': hora_cierre_intervalo,
#                                 'actividad': m,
#                                 'lugar': lugar.nombre
#                             }
#                             agenda.append(actividad)
#                             gustos_agregados.add(m.id)
#                             break
                        
#                         if lugar.horaApertura <= hora_inicio < lugar.horaCierre:
#                             if m.id not in gustos_agregados:
#                                 actividad = {
#                                     'dia': fecha_actual,
#                                     'hora_inicio': hora_inicio,
#                                     'hora_fin': hora_cierre_intervalo,
#                                     'actividad': m,
#                                     'lugar': lugar.nombre
#                                 }
#                                 agenda.append(actividad)
#                                 gustos_agregados.add(m.id)
#                                 break

#                     if datetime.strptime('00:00:00', '%H:%M:%S').time() <= hora_inicio <= datetime.strptime('04:00:00', '%H:%M:%S').time():
#                         break

#                     hora_inicio_datetime = datetime.combine(datetime.now().date(), hora_cierre_intervalo)  # Crear un objeto datetime
#                     hora_inicio_datetime += direccion  # Sumar la dirección al objeto datetime
#                     hora_inicio = hora_inicio_datetime.time() 
#                     inicioNumerico = hora_inicio.hour * 60 + hora_inicio.minute
                
#                 #!-CAMBIAR DELTA DAYS POR LA RESTA DE LAS FECHAS E INCREMENTAR A LA FECHA DESDE PARA PODER GUARDAR LA FECHA EN LA AGENDA
#                 fecha_actual += delta_dias
#             session.commit()
#             session.close()

#         self.saveAgenda(usuarioID,viajeID,fechaDesde,fechaHasta,horaInicio,horaFin,fechaHasta,agenda)
#         return agenda



# # print("Lista: "+ str(agenda))


#     def generarAgendaPersonalizada(self, usuarioID, viajeID, horariosElegidos, fechaDesde, fechaHasta, horaInicio, horaFin):
#         with Session(getEngine()) as session:
#             agenda_repo = AgendaRepository(session)
#             agenda = []

#             fecha_actual = datetime.strptime(fechaDesde, '%Y-%m-%d')
#             fecha_hasta = datetime.strptime(fechaHasta, '%Y-%m-%d')
#             delta_dias = timedelta(days=1)

#             while fecha_actual <= fecha_hasta:
#                 meGustas_ids = agenda_repo.buscarActividad(usuarioID, viajeID)

#                 if fecha_actual.date().strftime('%Y-%m-%d') in horariosElegidos:
#                     horario_inicio = datetime.strptime(horariosElegidos[fecha_actual.date().strftime('%Y-%m-%d')][0], '%H:%M:%S').time()
#                     horario_fin = datetime.strptime(horariosElegidos[fecha_actual.date().strftime('%Y-%m-%d')][1], '%H:%M:%S').time()
#                 else:
#                     horario_inicio = datetime.strptime(horaInicio, '%H:%M:%S').time() 
#                     horario_fin = datetime.strptime(horaFin, '%H:%M:%S').time()

#                 hora_actual = horario_inicio
#                 gustos_agregados = set()

#                 while hora_actual < horario_fin:
#                     for idx, m_id in enumerate(meGustas_ids):
#                         m = session.query(Actividad).get(m_id[0])
#                         lugar = agenda_repo.buscarLugar(m.id)

#                         minutos_duracion = m.duracion.hour * 60 + m.duracion.minute
#                         hora_cierre_intervalo = hora_actual.replace(hour=(hora_actual.hour + (minutos_duracion // 60)) % 24, minute=(hora_actual.minute + minutos_duracion % 60) % 60)

#                         siguiente_actividad = meGustas_ids[idx + 1] if idx + 1 < len(meGustas_ids) else None
#                         if siguiente_actividad:
#                             siguiente_actividad_obj = session.query(Actividad).get(siguiente_actividad[0])
#                             siguiente_lugar = agenda_repo.buscarLugar(siguiente_actividad_obj.id)

#                         direccion = self.calcularTiempoTraslado(lugar, siguiente_lugar, 'driving')
#                         if direccion:
#                             hora_inicio_datetime = datetime.combine(datetime.today(), hora_actual)
#                             hora_actual = (hora_inicio_datetime + direccion).time()
                        
#                         if lugar.tipo == 'restaurant' and horario_inicio in self.horas and lugar.horaApertura < horario_inicio < lugar.horaCierre:
#                             if m.id not in gustos_agregados:
#                                 actividad = {
#                                     'dia': fecha_actual,
#                                     'hora_inicio': horario_inicio,
#                                     'hora_fin': hora_cierre_intervalo,
#                                     'actividad': m,
#                                     'lugar': lugar.nombre
#                                 }
#                                 agenda.append(actividad)
#                                 gustos_agregados.add(m.id)
#                                 break
                        
#                         if lugar.horaApertura <= horario_inicio < lugar.horaCierre:
#                             if m.id not in gustos_agregados:
#                                 actividad = {
#                                     'dia': fecha_actual,
#                                     'hora_inicio': horario_inicio,
#                                     'hora_fin': hora_cierre_intervalo,
#                                     'actividad': m,
#                                     'lugar': lugar.nombre
#                                 }
#                                 agenda.append(actividad)
#                                 gustos_agregados.add(m.id)
#                                 break
                            
#                     if datetime.strptime('00:00:00', '%H:%M:%S').time() <= hora_actual <= datetime.strptime('04:00:00', '%H:%M:%S').time():
#                         break

#                     hora_inicio_datetime = datetime.combine(datetime.now().date(), hora_cierre_intervalo)  # Crear un objeto datetime
#                     hora_inicio_datetime += direccion  # Sumar la dirección al objeto datetime
#                     hora_actual = hora_inicio_datetime.time() 
                
#                 fecha_actual += delta_dias

#         return agenda

        
#generador de agenda diaria con dias ocupados, y horarios especificos
    def generarAgendaDiaria(self, usuarioID, destinoID, horariosElegidos, horariosOcupados,fechaDesde, fechaHasta, horaInicio, horaFin):
        with Session(getEngine()) as session:
            agenda_repo = AgendaRepository(session)
            agenda = []

            fecha_actual = datetime.strptime(fechaDesde, '%Y-%m-%d')
            fecha_hasta = datetime.strptime(fechaHasta, '%Y-%m-%d')
            delta_dias = timedelta(days=1)

            while fecha_actual <= fecha_hasta:
                actividadIds = agenda_repo.buscarActividad(usuarioID, destinoID)

                if fecha_actual.date().strftime('%Y-%m-%d') in horariosElegidos:
                    hora_actual = datetime.strptime(horariosElegidos[fecha_actual.date().strftime('%Y-%m-%d')][0], '%H:%M:%S').time()
                    horario_fin = datetime.strptime(horariosElegidos[fecha_actual.date().strftime('%Y-%m-%d')][1], '%H:%M:%S').time()
                else:
                    hora_actual = datetime.strptime(horaInicio, '%H:%M:%S').time() 
                    horario_fin = datetime.strptime(horaFin, '%H:%M:%S').time()

                gustos_agregados = set()

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

                        siguiente_actividad = actividadIds[idx + 1] if idx + 1 < len(actividadIds) else None
                        if siguiente_actividad:
                            siguiente_actividad_obj = session.query(Actividad).get(siguiente_actividad[0])
                            siguiente_lugar = agenda_repo.buscarLugar(siguiente_actividad_obj.id)

                        direccion = self.calcularTiempoTraslado(lugar, siguiente_lugar, 'driving')
                        if direccion:
                            hora_inicio_datetime = datetime.combine(datetime.today(), hora_actual)
                            hora_actual = (hora_inicio_datetime + direccion).time()
                        
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
                
                #!-CAMBIAR DELTA DAYS POR LA RESTA DE LAS FECHAS E INCREMENTAR A LA FECHA DESDE PARA PODER GUARDAR LA FECHA EN LA AGENDA
                fecha_actual += delta_dias
                print(fecha_actual)

            #session.commit()
            #session.close()

        self.saveAgenda(usuarioID,destinoID,fechaDesde,fechaHasta,horaInicio,horaFin,fechaHasta,agenda)
        return agenda