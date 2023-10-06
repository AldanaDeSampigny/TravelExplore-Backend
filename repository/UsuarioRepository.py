from sqlalchemy import func

from ..models.Actividad import Actividad
from ..models.ActividadAgenda import ActividadAgenda

from ..models.AgendaDiaria import AgendaDiaria

from ..models.Itinerario import Itinerario
from    sqlalchemy import select
from ..models.Viaje import Viaje
from ..models.AgendaViaje import AgendaViaje
from ..models.Usuario import Usuario
from ..models.Categoria import Categoria
from ..models.UsuarioCategoria import UsuarioCategoria
from sqlalchemy.orm import sessionmaker

class UsuarioRepository:
    def __init__(self, db_session): #esto seria un constructor
        self.db_session = db_session

    def getUsuarios(self):
        usuarios = self.db_session.query(Usuario).all()
        
        return usuarios

    def getAgendaUsuario(self,usuarioID):  
        max_av_id = self.db_session.query(func.max(AgendaViaje.id)).scalar()

        franki = (
            self.db_session.query(ActividadAgenda.id_agenda,
                AgendaDiaria.dia,
                Actividad.id,
                Actividad.nombre,
                AgendaDiaria.horaInicio,
                AgendaDiaria.horaFin,
            )
            .join(AgendaDiaria, AgendaDiaria.id == ActividadAgenda.id_agenda)
            .join(Actividad, Actividad.id == ActividadAgenda.id_actividad)
            .join(AgendaViaje, AgendaDiaria.id_agenda_viaje == AgendaViaje.id)
            .join(Itinerario, Itinerario.id == AgendaDiaria.itinerario_id)
            .join(Viaje, Viaje.id == Itinerario.id_viaje)
            .join(Usuario, Usuario.id == Viaje.id_usuario)
            .filter(AgendaViaje.id == max_av_id)
            .filter(Usuario.id == usuarioID)
        )
     
        return franki
    #!volver a pensar query 
    def obtenerAgendasUsuario(self,usuarioID):
        agendas = (
            self.db_session.query(
                AgendaViaje.id,  # O el campo que identifica de manera única cada agenda
                AgendaDiaria.dia,
                Actividad.id,
                Actividad.nombre,
                AgendaDiaria.horaInicio,
                AgendaDiaria.horaFin,
                Viaje.fechaDesde,
                Viaje.fechaHasta
            )
            .join(AgendaDiaria, AgendaDiaria.id == ActividadAgenda.id_agenda)
            .join(Actividad, Actividad.id == ActividadAgenda.id_actividad)
            .join(AgendaViaje, AgendaDiaria.id_agenda_viaje == AgendaViaje.id)
            .join(Itinerario, Itinerario.id == AgendaDiaria.itinerario_id)
            .join(Viaje, Viaje.id == Itinerario.id_viaje)
            .join(Usuario, Usuario.id == Viaje.id_usuario)
            .filter(Usuario.id == usuarioID)
            # Elimina el filtro de fecha si deseas obtener todas las agendas sin restricciones de fecha
            # .filter(Viaje.fechaDesde >= '2023-10-05' and Viaje.fechaHasta <= '2023-10-07')
            .group_by(AgendaViaje.id)  # Agrupa por el campo que identifica cada agenda
        )
        return agendas.all()