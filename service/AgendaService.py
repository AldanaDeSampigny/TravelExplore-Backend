from ..repository.MeGustaRepository import MeGustaRepository
from ..models.MeGustas import MeGustas
from ..models.Agendas import Agendas
from ..models.DiaViaje import DiaViaje
from ..models.Actividad import Actividad
from ..repository.AgendaRepository import AgendaRepository
from ..bd.conexion import getEngine
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

class AgendaService:
    def __init__(self, db_session):
        self.db_session = db_session


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
                session.close()


    def generar_agenda(self, usuarioID, viajeID):
        with Session(getEngine()) as session:
            agenda_repo = AgendaRepository(session)
            agenda = []
            horas = {datetime.strptime('09:00:00', '%H:%M:%S').time(): datetime.strptime('11:00:00', '%H:%M:%S').time(),
                    datetime.strptime('12:00:00', '%H:%M:%S').time(): datetime.strptime('14:00:00', '%H:%M:%S').time(),
                    datetime.strptime('17:00:00', '%H:%M:%S').time(): datetime.strptime('19:00:00', '%H:%M:%S').time(),
                    datetime.strptime('21:00:00', '%H:%M:%S').time(): datetime.strptime('23:00:00', '%H:%M:%S').time()}

            dias_semana = list(range(1, 8))
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

            return agenda

    def generarAgendaPersonalizada(self, usuarioID, viajeID, horariosElegidos):
        with Session(getEngine()) as session:
            agenda_repo = AgendaRepository(session)
            agenda = []
            dias_semana = list(range(1, 8))
            horas = {
                datetime.strptime('09:00:00', '%H:%M:%S').time(): datetime.strptime('11:00:00', '%H:%M:%S').time(),
                datetime.strptime('12:00:00', '%H:%M:%S').time(): datetime.strptime('14:00:00', '%H:%M:%S').time(),
                datetime.strptime('17:00:00', '%H:%M:%S').time(): datetime.strptime('19:00:00', '%H:%M:%S').time(),
                datetime.strptime('21:00:00', '%H:%M:%S').time(): datetime.strptime('23:00:00', '%H:%M:%S').time()
            }

            for dia in dias_semana:
                meGustas_ids = agenda_repo.buscarGustos(usuarioID, viajeID)

                if dia in horariosElegidos:
                    horario_inicio = datetime.strptime(horariosElegidos[dia][0], '%H:%M:%S').time()
                    horario_fin = datetime.strptime(horariosElegidos[dia][1], '%H:%M:%S').time()
                else:
                    horario_inicio = datetime.strptime('14:00:00', '%H:%M:%S').time()
                    horario_fin = datetime.strptime('23:00:00', '%H:%M:%S').time()

                hora_actual = horario_inicio
                gustos_agregados = set()

                while hora_actual < horario_fin:
                    for m_id in meGustas_ids:
                        m = session.query(MeGustas).get(m_id[0])
                        minutos_duracion = m.duracion.hour * 60 + m.duracion.minute
                        hora_cierre_intervalo = datetime.combine(datetime.today(), hora_actual) + timedelta(minutes=minutos_duracion)

                        if m.tipo == 'restaurant' and hora_actual in horas and m.horarioApertura < hora_actual < m.horarioCierre:
                            if m.id not in gustos_agregados:
                                actividad = {
                                    'dia': dia,
                                    'hora_inicio': hora_actual,
                                    'hora_fin': hora_cierre_intervalo.time(),
                                    'actividad': m
                                }
                                agenda.append(actividad)
                                gustos_agregados.add(m.id)
                                break

                        if m.horarioApertura < hora_actual < m.horarioCierre:
                            if m.id not in gustos_agregados:
                                actividad = {
                                    'dia': dia,
                                    'hora_inicio': hora_actual,
                                    'hora_fin': hora_cierre_intervalo.time(),
                                    'actividad': m
                                }
                                agenda.append(actividad)
                                gustos_agregados.add(m.id)
                                break
                    if datetime.strptime('00:00:00', '%H:%M:%S').time() <= hora_actual <= datetime.strptime('04:00:00', '%H:%M:%S').time():
                        break

                    hora_actual = (hora_cierre_intervalo + timedelta(minutes=30)).time()
        return agenda


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
   
            return agenda

   

    
