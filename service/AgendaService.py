from ..models.usuario import usuarios
from ..repository.meGustaRepository import meGustaRepository
from ..models.meGusta import meGustas
from ..repository.AgendaRepository import AgendaRepository
from datetime import datetime, timedelta
from ..bd.conexion import getEngine
from sqlalchemy.orm import Session

class AgendaService:
    def __init__(self, db_session):
        self.db_session = db_session

    def generar_agenda(self, usuarioID, viajeID):
        with Session(getEngine()) as session:
            print(usuarioID, viajeID, "service")
            agenda_repo = AgendaRepository(session)
            meGustas_ids = agenda_repo.buscarGustos(usuarioID, viajeID)
            agenda = []
            horas = {datetime.strptime('09:00:00', '%H:%M:%S').time(): datetime.strptime('11:00:00', '%H:%M:%S').time(),
                    datetime.strptime('12:00:00', '%H:%M:%S').time(): datetime.strptime('15:00:00', '%H:%M:%S').time(),
                    datetime.strptime('17:00:00', '%H:%M:%S').time(): datetime.strptime('19:00:00', '%H:%M:%S').time(),
                    datetime.strptime('21:00:00', '%H:%M:%S').time(): datetime.strptime('23:00:00', '%H:%M:%S').time()}

            dias_semana = list(range(1, 8))

            for dia in dias_semana:
                hora_inicio = datetime.strptime('14:00:00', '%H:%M:%S').time()  # Convierte la hora inicial a datetime.time
                while hora_inicio < datetime.strptime('23:00:00', '%H:%M:%S').time():
                    for m_id in meGustas_ids:
                        m = session.query(meGustas).get(m_id[0])

                        horario_apertura = m.horarioApertura
                        horario_cierre = m.horarioCierre
                        hora_actual = datetime.combine(datetime.today(), hora_inicio)
                        minutos_duracion = m.duracion.hour * 60 + m.duracion.minute
                        hora_cierre_intervalo = hora_actual + timedelta(minutes=minutos_duracion)

                        if m.tipo == 'restaurant' and hora_inicio in horas and horario_apertura < hora_inicio < horario_cierre:
                            
                            actividad_data = {
                                'dia': dia,
                                'hora_inicio': hora_inicio,
                                'hora_fin': hora_cierre_intervalo,
                                'actividad': m
                            }
                            agenda.append(actividad_data)
                            break
                        
                        if horario_apertura < hora_inicio < horario_cierre:
                            actividad_data = {
                                'dia': dia,
                                'hora_inicio': hora_inicio,
                                'hora_fin': hora_cierre_intervalo,
                                'actividad': m
                            }
                            agenda.append(actividad_data)
                            break
                        
                    if hora_inicio == datetime.strptime('23:00:00', '%H:%M:%S').time():
                        break
                    
                    hora_cierre_intervalo += timedelta(minutes=30)
                    hora_inicio = hora_cierre_intervalo.time()

            return agenda

    def horariosDias(fechaDesde, fechaHasta, horaDesde, horaHasta):
            diasHorarios = {}
            
            fechaDesde = datetime.strptime(fechaDesde, "%Y-%m-%d")
            fechaHasta = datetime.strptime(fechaHasta, "%Y-%m-%d")

            # Inicializa un contador de días
            fechaActual = fechaDesde

            while fechaActual <= fechaHasta:
                # Obtiene el nombre del día de la semana
                diaSemana = fechaActual.strftime("%A")

                # Agrega el rango horario al diccionario
                diasHorarios[diaSemana] = (horaDesde, horaHasta)

                # Avanza al siguiente día
                fechaActual += timedelta(days=1)

            return diasHorarios

    def generarAgendaPersonalizada(usuarioID, viajeID,horariosDias):
        with Session(getEngine()) as session:
            meGusta_repo = meGustaRepository(session)
            meGustas = meGusta_repo.buscarGustas(usuarioID, viajeID)
            con = 1
            agenda = {}
        
            for dia, (hora_inicio, hora_fin) in horariosDias.items():
                hora = hora_inicio
                agenda[con] = {}  # Inicializa el diccionario del día
                while hora <= hora_fin:
                    for m in meGustas:
                        if m.tipo == 'restaurant':
                            if (hora, hora + m.duracion) not in agenda[con]:
                                agenda[con][(hora, hora + m.duracion)] = m.id

                        if m.horaApertura < hora < m.horaCierre:
                            if (hora, hora + m.duracion) not in agenda[con]:
                                agenda[con][(hora, hora + m.duracion)] = m.id
                        hora += m.duracion + 0.5
                    con += 1
            return agenda 
        
    def buscarViaje(self, usuario_id):
        # Consulta SQL utilizando SQLAlchemy
        query = self.db_session.query(meGustas.id).\
            join(viajes, meGustas.viaje_id == viajes.id).\
            join(usuarios, viajes.usuario_id == usuarios.id).\
            filter(usuarios.id == usuario_id)

        # Ejecutar la consulta y obtener los resultados
        viajes  = query.all()

        return viajes


    #viaje = buscarViaje(usuarioID=123)
    #fechaDesdeViaje = datetime.strptime(viaje.fechaDesde, "%Y-%m-%d")
    #fechaHastaViaje = datetime.strptime(viaje.fechaHasta, "%Y-%m-%d")

    #while  fechaDesdeViaje <= fechaHastaViaje:
    #    if not horariosDias:  # si el diccionario está vacío
    #        generar_agenda(usuarioID=123, viajeID=321)  # llamada a generarAgenda
    #    else:
    #        generarAgendaPersonalizada(usuarioID=123, viajeID=543, horariosDias=("2023-05-12", "2023-05-19", "08:00:00", "15:00:00"))
    #fechaDesdeViaje += timedelta(days=1)