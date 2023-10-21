from sqlalchemy import func

from ..models.Actividad import Actividad
from ..models.ActividadAgenda import ActividadAgenda
from ..models.Ciudad import Ciudad

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

    def getAgendaUsuario(self,usuarioID,idAgenda):  
        #max_av_id = self.db_session.query(func.max(AgendaViaje.id)).scalar()

        agenda = (
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
            .filter(Usuario.id == usuarioID)
            .filter(AgendaViaje.id == idAgenda)
        )
     
        return agenda
    #query para mstrar una agenda del usuario
    def obtenerAgendasUsuario(self,usuarioID):
        query = (self.db_session.query(ActividadAgenda.id_agenda,
                AgendaDiaria.dia,
                Actividad.id,
                Actividad.nombre,
                AgendaDiaria.horaInicio,
                AgendaDiaria.horaFin,
                Viaje.fechaDesde,
                Viaje.fechaHasta,
                Ciudad.nombre
            )
            .join(AgendaDiaria, AgendaDiaria.id == ActividadAgenda.id_agenda)
            .join(Actividad, Actividad.id == ActividadAgenda.id_actividad)
            .join(AgendaViaje, AgendaDiaria.id_agenda_viaje == AgendaViaje.id)
            .join(Itinerario, Itinerario.id == AgendaDiaria.itinerario_id)
            .join(Ciudad, Ciudad.id == Itinerario.id_ciudad)
            .join(Viaje, Viaje.id == Itinerario.id_viaje)
            .join(Usuario, Usuario.id == Viaje.id_usuario)
            .filter(Usuario.id == usuarioID).all()
        )
        return query
    
    def todasLasAgendasUsuario(self,usuarioID):
        agendas = (self.db_session.query(
                Itinerario.fechaDesde,
                Itinerario.fechaHasta,
                Ciudad.nombre,
                AgendaDiaria.id_agenda_viaje
            )
            .join(AgendaViaje, AgendaDiaria.id_agenda_viaje == AgendaViaje.id)
            .join(Itinerario, Itinerario.id == AgendaDiaria.itinerario_id)
            .join(Ciudad, Ciudad.id == Itinerario.id_ciudad)
            .join(Viaje, Viaje.id == Itinerario.id_viaje)
            .join(Usuario, Usuario.id == Viaje.id_usuario)
            .filter(Usuario.id == usuarioID)
            .group_by(Itinerario.fechaDesde, Itinerario.fechaHasta, Ciudad.nombre, AgendaDiaria.id_agenda_viaje)
            .order_by((Itinerario.fechaDesde.desc()))
        )
        return agendas
    


   