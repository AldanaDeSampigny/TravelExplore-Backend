from sqlalchemy import func

from ..models.Actividad import Actividad
from ..models.ActividadAgenda import ActividadAgenda

from ..models.AgendaDiaria import AgendaDiaria

from ..models.Itinerario import Itinerario

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
        usuarios = self.db_session.query(Usuario)
        
        return usuarios.all()

    def getAgendaUsuario(self,usuarioID):
        subquery = self.db_session.query(func.max(AgendaViaje.id)).\
                join(AgendaDiaria, AgendaDiaria.id == AgendaViaje.id).\
                join(Itinerario, AgendaDiaria.itinerario_id == Itinerario.id).\
                join(Viaje, Itinerario.id_viaje == Viaje.id).\
                join(Usuario, Viaje.id_usuario == Usuario.id).\
                filter(Usuario.id == usuarioID).group_by(Usuario.id)

        indiceAgenda = subquery.all()[0][0]
        
        print(str(subquery.all()))
        query = self.db_session.query.(AgendaDiaria.dia, Actividad.id, Actividad.nombre, AgendaDiaria.horaInicio, AgendaDiaria.horaFin).distinct()\
                join(ActividadAgenda, AgendaDiaria.id == ActividadAgenda.id_agenda).\
                join(Actividad, ActividadAgenda.id_actividad == Actividad.id).\
                filter(AgendaViaje.id == indiceAgenda)

        result = query.all()

        return result
    
    # def getUsuarioCategoria(self, usuarioID):
    #     categorias = self.db_session.query(Categoria.id).\
    #         join (Categoria, Categoria.id == UsuarioCategoria.id_categorias).\
    #         join (Usuario, Usuario.id == UsuarioCategoria.id_usuarios).\
    #         filter(Usuario.id == usuarioID).all()

    #     return categorias