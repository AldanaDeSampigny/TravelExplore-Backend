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
    horas = {datetime.strptime('09:00:00', '%H:%M:%S').time(): datetime.strptime('11:00:00', '%H:%M:%S').time(),
                    datetime.strptime('12:00:00', '%H:%M:%S').time(): datetime.strptime('14:00:00', '%H:%M:%S').time(),
                    datetime.strptime('17:00:00', '%H:%M:%S').time(): datetime.strptime('19:00:00', '%H:%M:%S').time(),
                    datetime.strptime('21:00:00', '%H:%M:%S').time(): datetime.strptime('23:00:00', '%H:%M:%S').time()}
    
    def __init__(self, db_session):
        self.db_session = db_session

    def saveAgenda(self, idUsuario,idCiudad,fechaDesde,fechaHasta, horaInicio, horaFin, dia):
        with Session(getEngine()) as session:
            nuevoViaje =  Viaje()
            nuevoViaje.id_usuario=  idUsuario
            nuevoViaje.fechaDesde = fechaDesde
            nuevoViaje.fechaHasta = fechaHasta
            
            try:
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

                actividad = Actividad()
                actividad.id_agenda_diaria = 3
                    
                session.commit()
                #session.update(actividad)
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
                print(direccion)
            else:
                direccion = None
            return direccion


    def generar_agenda(self, usuarioID, viajeID, fechaDesde, fechaHasta, horaInicio, horaFin):
        with Session(getEngine()) as session:
            agenda_repo = AgendaRepository(session)
            agenda = []

            hora_inicio = datetime.strptime(horaInicio, '%H:%M:%S').time() 
            hora_cierre_intervalo = datetime.strptime('00:00:00', '%H:%M:%S').time() 
            inicioNumerico = hora_inicio.hour * 60 + hora_inicio.minute 
            finNumerico = datetime.strptime(horaFin, '%H:%M:%S').time().hour * 60 + datetime.strptime(horaFin, '%H:%M:%S').time().minute

            fecha_actual = datetime.strptime(fechaDesde, '%Y-%m-%d')
            fecha_hasta = datetime.strptime(fechaHasta, '%Y-%m-%d')
            delta_dias = timedelta(days=1)

            while fecha_actual <= fecha_hasta:
                meGustas_ids = agenda_repo.buscarActividad(usuarioID, viajeID)
                hora_inicio = datetime.strptime(horaInicio, '%H:%M:%S').time() 
                inicioNumerico = hora_inicio.hour * 60 + hora_inicio.minute 
                gustos_agregados = set()
                while inicioNumerico < finNumerico:
                    for idx, m_id in enumerate(meGustas_ids):

                        m = session.query(Actividad).get(m_id[0])
                        lugar = agenda_repo.buscarLugar(m.id)

                        minutos_duracion = m.duracion.hour * 60 + m.duracion.minute
                        hora_cierre_intervalo = hora_inicio.replace(hour=(hora_inicio.hour + (minutos_duracion // 60)) % 24, minute=(hora_inicio.minute + minutos_duracion % 60) % 60)

                        siguiente_actividad = meGustas_ids[idx + 1] if idx + 1 < len(meGustas_ids) else None
                        if siguiente_actividad:
                            siguiente_actividad_obj = session.query(Actividad).get(siguiente_actividad[0])
                            siguiente_lugar = agenda_repo.buscarLugar(siguiente_actividad_obj.id)

                        direccion = self.calcularTiempoTraslado(lugar, siguiente_lugar, 'driving')
                        if direccion:
                            hora_inicio_datetime = datetime.combine(datetime.today(), hora_inicio)
                            hora_inicio = (hora_inicio_datetime + direccion).time()

                        #PROBLEMA, NO SE METE EN ESTE IF
                        #podria traer una query que traiga un lugar de tipo restaurante y los meta aca
                        if lugar.tipo == 'restaurant' and hora_inicio in self.horas and lugar.horaApertura <= hora_inicio < lugar.horaCierre:
                            if m.id not in gustos_agregados:
                                actividad = {
                                'dia': fecha_actual,
                                'hora_inicio': hora_inicio,
                                'hora_fin': hora_cierre_intervalo,
                                'actividad': m,
                                'lugar': lugar.nombre
                            }
                            agenda.append(actividad)
                            gustos_agregados.add(m.id)
                            break
                        
                        if lugar.horaApertura <= hora_inicio < lugar.horaCierre:
                            if m.id not in gustos_agregados:
                                actividad = {
                                    'dia': fecha_actual,
                                    'hora_inicio': hora_inicio,
                                    'hora_fin': hora_cierre_intervalo,
                                    'actividad': m,
                                    'lugar': lugar.nombre
                                }
                                agenda.append(actividad)
                                gustos_agregados.add(m.id)
                                break

                    if datetime.strptime('00:00:00', '%H:%M:%S').time() <= hora_inicio <= datetime.strptime('04:00:00', '%H:%M:%S').time():
                        break

                    hora_inicio_datetime = datetime.combine(datetime.now().date(), hora_cierre_intervalo)  # Crear un objeto datetime
                    hora_inicio_datetime += direccion  # Sumar la dirección al objeto datetime
                    hora_inicio = hora_inicio_datetime.time() 
                    inicioNumerico = hora_inicio.hour * 60 + hora_inicio.minute

                #!-CAMBIAR DELTA DAYS POR LA RESTA DE LAS FECHAS E INCREMENTAR A LA FECHA DESDE PARA PODER GUARDAR LA FECHA EN LA AGENDA
                self.saveAgenda(usuarioID,viajeID,fechaDesde,fechaHasta,horaInicio,horaFin,fechaHasta)
                fecha_actual += delta_dias

            return agenda



    def generarAgendaPersonalizada(self, usuarioID, viajeID, horariosElegidos, fechaDesde, fechaHasta, horaInicio, horaFin):
        with Session(getEngine()) as session:
            agenda_repo = AgendaRepository(session)
            agenda = []

            fecha_actual = datetime.strptime(fechaDesde, '%Y-%m-%d')
            fecha_hasta = datetime.strptime(fechaHasta, '%Y-%m-%d')
            delta_dias = timedelta(days=1)

            while fecha_actual <= fecha_hasta:
                meGustas_ids = agenda_repo.buscarActividad(usuarioID, viajeID)

                if fecha_actual.date().strftime('%Y-%m-%d') in horariosElegidos:
                    horario_inicio = datetime.strptime(horariosElegidos[fecha_actual.date().strftime('%Y-%m-%d')][0], '%H:%M:%S').time()
                    horario_fin = datetime.strptime(horariosElegidos[fecha_actual.date().strftime('%Y-%m-%d')][1], '%H:%M:%S').time()
                else:
                    horario_inicio = datetime.strptime(horaInicio, '%H:%M:%S').time() 
                    horario_fin = datetime.strptime(horaFin, '%H:%M:%S').time()

                hora_actual = horario_inicio
                gustos_agregados = set()

                while hora_actual < horario_fin:
                    for idx, m_id in enumerate(meGustas_ids):
                        m = session.query(Actividad).get(m_id[0])
                        lugar = agenda_repo.buscarLugar(m.id)

                        minutos_duracion = m.duracion.hour * 60 + m.duracion.minute
                        hora_cierre_intervalo = hora_actual.replace(hour=(hora_actual.hour + (minutos_duracion // 60)) % 24, minute=(hora_actual.minute + minutos_duracion % 60) % 60)

                        siguiente_actividad = meGustas_ids[idx + 1] if idx + 1 < len(meGustas_ids) else None
                        if siguiente_actividad:
                            siguiente_actividad_obj = session.query(Actividad).get(siguiente_actividad[0])
                            siguiente_lugar = agenda_repo.buscarLugar(siguiente_actividad_obj.id)

                        direccion = self.calcularTiempoTraslado(lugar, siguiente_lugar, 'driving')
                        if direccion:
                            hora_inicio_datetime = datetime.combine(datetime.today(), hora_actual)
                            hora_actual = (hora_inicio_datetime + direccion).time()
                        
                        if lugar.tipo == 'restaurant' and horario_inicio in self.horas and lugar.horaApertura < horario_inicio < lugar.horaCierre:
                            if m.id not in gustos_agregados:
                                actividad = {
                                    'dia': fecha_actual,
                                    'hora_inicio': horario_inicio,
                                    'hora_fin': hora_cierre_intervalo,
                                    'actividad': m,
                                    'lugar': lugar.nombre
                                }
                                agenda.append(actividad)
                                gustos_agregados.add(m.id)
                                break
                        
                        if lugar.horaApertura <= horario_inicio < lugar.horaCierre:
                            if m.id not in gustos_agregados:
                                actividad = {
                                    'dia': fecha_actual,
                                    'hora_inicio': horario_inicio,
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

        return agenda
"""
    def guardarAgendaEnBd(self, agenda):
        with Session(getEngine()) as session:
            agendaNueva = Agendas()
            agendaNueva.id = 105
            agendaNueva.horaInicio = "12:00:00"
            agendaNueva.horaFin = "15:00:00"
            agendaNueva.fechaDesde = "2023-05-15"
            agendaNueva.fechaHasta = "2023-05-17"
            agendaNueva.usuario_id = 1

            try:
                session.add(agendaNueva)
                session.commit()
            
            except Exception as e:
                # En caso de error, realiza un rollback
                session.rollback()
                raise e
            
            finally:
                # Cierra la sesión
                session.close()"""


"""
    #viaje = buscarViaje(usuarioID=123)
    #fechaDesdeViaje = datetime.strptime(viaje.fechaDesde, "%Y-%m-%d")
    #fechaHastaViaje = datetime.strptime(viaje.fechaHasta, "%Y-%m-%d")

    #while  fechaDesdeViaje <= fechaHastaViaje:
    #    if not horariosDias:  # si el diccionario está vacío
    #        generar_agenda(usuarioID=123, viajeID=321)  # llamada a generarAgenda
    #    else:
    #        generarAgendaPersonalizada(usuarioID=123, viajeID=543, horariosDias=("2023-05-12", "2023-05-19", "08:00:00", "15:00:00"))
    #fechaDesdeViaje += timedelta(days=1)

    def generar_agendaOcupada(self, usuarioID, viajeID, diasOcupados):
        with Session(getEngine()) as session:
            agenda_repo = AgendaRepository(session)
            agenda = []
            dias_semana = list(range(1, 8))
            horas = {datetime.strptime('09:00:00', '%H:%M:%S').time(): datetime.strptime('11:00:00', '%H:%M:%S').time(),
                    datetime.strptime('12:00:00', '%H:%M:%S').time(): datetime.strptime('14:00:00', '%H:%M:%S').time(),
                    datetime.strptime('17:00:00', '%H:%M:%S').time(): datetime.strptime('19:00:00', '%H:%M:%S').time(),
                    datetime.strptime('21:00:00', '%H:%M:%S').time(): datetime.strptime('23:00:00', '%H:%M:%S').time()}

            hora_inicio = datetime.strptime('14:00:00', '%H:%M:%S').time() 
            inicioNumerico = hora_inicio.hour * 60 + hora_inicio.minute 
            finNumerico = datetime.strptime('23:00:00', '%H:%M:%S').time().hour * 60 + datetime.strptime('23:00:00', '%H:%M:%S').time().minute

            for dia in dias_semana:
                
                meGustas_ids = agenda_repo.buscarGustos(usuarioID, viajeID)
                hora_inicio = datetime.strptime('14:00:00', '%H:%M:%S').time() 
                inicioNumerico = hora_inicio.hour * 60 + hora_inicio.minute 
                gustos_agregados = set()

                while inicioNumerico < finNumerico:
                    for m_id in meGustas_ids:

                        m = session.query(MeGustas).get(m_id[0])
                        minutos_duracion = m.duracion.hour * 60 + m.duracion.minute
                        hora_cierre_intervalo = (datetime.combine(datetime.today(), hora_inicio)) + timedelta(minutes=minutos_duracion)
                        
                        if dia in diasOcupados:
                            inicio = datetime.strptime(diasOcupados[dia][0], '%H:%M:%S').time()
                            fin = datetime.strptime(diasOcupados[dia][1], '%H:%M:%S').time()
                            if inicio <= hora_inicio <= fin or inicio <= hora_cierre_intervalo.time() <= fin:
                                print("dia: ",dia ,"inicio: ", hora_inicio, "fin: ", hora_cierre_intervalo, "gusto: ", m.nombre)
                                hora_cierre_intervalo = (datetime.combine(datetime.today(), hora_inicio))
                                #break
                            else:
                                if m.tipo == 'restaurant' and hora_inicio in horas and m.horarioApertura < hora_inicio < m.horarioCierre:
                                    if m.id not in gustos_agregados:
                                        actividad = {
                                            'dia': dia,
                                            'hora_inicio': hora_inicio,
                                            'hora_fin': hora_cierre_intervalo,
                                            'actividad': m
                                        }
                                        agenda.append(actividad)
                                        gustos_agregados.add(m.id)
                                        break
                                    
                                if m.horarioApertura < hora_inicio < m.horarioCierre:
                                    if m.id not in gustos_agregados:
                                        actividad = {
                                            'dia': dia,
                                            'hora_inicio': hora_inicio,
                                            'hora_fin': hora_cierre_intervalo,
                                            'actividad': m
                                        }
                                        agenda.append(actividad)
                                        gustos_agregados.add(m.id)
                                        break
                        else:
                            if m.tipo == 'restaurant' and hora_inicio in horas and m.horarioApertura < hora_inicio < m.horarioCierre:
                                if m.id not in gustos_agregados:
                                    actividad = {
                                        'dia': dia,
                                        'hora_inicio': hora_inicio,
                                        'hora_fin': hora_cierre_intervalo,
                                        'actividad': m
                                    }
                                    agenda.append(actividad)
                                    gustos_agregados.add(m.id)
                                    break
                                
                            if m.horarioApertura < hora_inicio < m.horarioCierre:
                                if m.id not in gustos_agregados:
                                    actividad = {
                                        'dia': dia,
                                        'hora_inicio': hora_inicio,
                                        'hora_fin': hora_cierre_intervalo,
                                        'actividad': m
                                    }
                                    agenda.append(actividad)
                                    gustos_agregados.add(m.id)
                                    break

                    if datetime.strptime('00:00:00', '%H:%M:%S').time() <= hora_inicio <= datetime.strptime('04:00:00', '%H:%M:%S').time():
                        break

                    hora_inicio = (hora_cierre_intervalo + timedelta(minutes=30)).time()
                    inicioNumerico = hora_inicio.hour * 60 + hora_inicio.minute
   
            return agenda """