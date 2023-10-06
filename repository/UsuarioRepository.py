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
    """    subQueryUsuario = select([Usuario.id]).where(Usuario.id == usuarioID).as_scalar()

        subQueryAgendaViaje = select([func.max(AgendaViaje.id)]).as_scalar()
            #         group_by(Categoria.id, Actividad.id).\
            # order_by(func.max(Actividad.valoracion))
        
        franki = self.db_session.query(AgendaDiaria.id ,Actividad.id, Actividad.nombre, AgendaDiaria.horaInicio, AgendaDiaria.horaFin).\
                join(Usuario, Usuario.id == Viaje.id_usuario).\
                join(Itinerario, Itinerario.id_viaje == Viaje.id).\
                join(AgendaDiaria, AgendaDiaria.itinerario_id == Itinerario.id).\
                join(AgendaViaje, AgendaViaje.id == AgendaDiaria.id_agenda_viaje).\
                join(ActividadAgenda, ActividadAgenda.id_agenda ==  AgendaDiaria.id).\
                join(Actividad, Actividad.id == ActividadAgenda.id_actividad).\
                filter(AgendaViaje.id.in_(subQueryAgendaViaje)).\
                filter(Usuario.id.in_(subQueryUsuario))
                #ilter(Categoria.id.in_(subquery_cat_ids))
        return franki.all() """
    
