from ..models.ActividadLugar import ActividadLugar
from ..models.AgendaViaje import AgendaViaje
from ..models.AgendaDiaria import AgendaDiaria
from ..models.Itinerario import Itinerario
from ..models.ActividadAgenda import ActividadAgenda
from ..models.Actividad import Actividad
from ..models.ActividadCategoria import ActividadCategoria
from ..models.Categoria import Categoria
from ..models.UsuarioCategoria import UsuarioCategoria
from ..models.Lugar import Lugar
from ..models.Ciudad import Ciudad

from sqlalchemy.orm import Session

from sqlalchemy.orm import sessionmaker
from ..models.Usuario import Usuario
from sqlalchemy import func

class AgendaRepository:
    def __init__(self, db_session): #esto seria un constructor
        self.db_session = db_session

    def crear_agenda(self, horaInicio, horaFin): 
        agenda = agenda(hora_inicio= horaInicio, hora_fin= horaFin)
        self.db_session.add(agenda)
        self.db_session.commit()
        return agenda
    
    def getActividadAgenda(self, idActividad, idAgenda):
        actividadAgenda = self.db_session.query(ActividadAgenda).\
            filter(ActividadAgenda.id_actividad == idActividad).\
            filter(ActividadAgenda.id_agenda == idAgenda).first()
        
        return actividadAgenda

    def buscarActividad(self, usuarioID, ciudadID):
        subquery_cat_ids = self.db_session.query(Categoria.id).\
            join(UsuarioCategoria, Categoria.id == UsuarioCategoria.id_categorias).\
            filter(UsuarioCategoria.id_usuario == usuarioID).\
            subquery()

        query = self.db_session.query(Actividad.id).\
            join(ActividadCategoria, Actividad.id == ActividadCategoria.id_actividad).\
            join(Categoria, ActividadCategoria.id_categoria == Categoria.id).\
            join(UsuarioCategoria, Categoria.id == UsuarioCategoria.id_categorias).\
            join(Usuario, UsuarioCategoria.id_usuario == Usuario.id).\
            join(ActividadLugar, ActividadLugar.id_actividad == Actividad.id).\
            join(Lugar, ActividadLugar.id_lugar == Lugar.id).\
            join(Ciudad, Lugar.id_ciudad == Ciudad.id).\
            filter(Usuario.id == usuarioID).\
            filter(Ciudad.id == ciudadID).\
            filter(Categoria.id.in_(subquery_cat_ids)).\
            group_by(Categoria.id, Actividad.id).\
            order_by(func.max(Actividad.valoracion))

        result = query.all()  # Ejecutar la consulta

        return result

    def buscarLugares(self, actividadID, destinoID):
        lugares = self.db_session.query(Lugar).\
            join(ActividadLugar, ActividadLugar.id_lugar == Lugar.id).\
            join(Actividad, Actividad.id == ActividadLugar.id_actividad).\
            filter(Lugar.id_ciudad == destinoID).\
            filter(Actividad.id == actividadID).\
            group_by(Lugar.id).\
            order_by(func.max(Lugar.valoracion)).all()
        
        return lugares
        

    def buscarActividadRestaurant(self, usuarioID, ciudadID):
        subquery_cat_ids = self.db_session.query(Categoria.id).\
            join(UsuarioCategoria, Categoria.id == UsuarioCategoria.id_categorias).\
            filter(UsuarioCategoria.id_usuario == usuarioID).\
            subquery()

        query = self.db_session.query(Actividad).\
            join(ActividadCategoria, Actividad.id == ActividadCategoria.id_actividad).\
            join(Categoria, ActividadCategoria.id_categoria == Categoria.id).\
            join(UsuarioCategoria, Categoria.id == UsuarioCategoria.id_categorias).\
            join(Usuario, UsuarioCategoria.id_usuario == Usuario.id).\
            join(Lugar, Actividad.id_lugar == Lugar.id).\
            join(Ciudad, Lugar.id_ciudad == Ciudad.id).\
            filter(Usuario.id == usuarioID).\
            filter(Ciudad.id == ciudadID).\
            filter(Lugar.tipo == 'restaurant').\
            filter(Categoria.id.in_(subquery_cat_ids)).\
            order_by(func.random())  # Ordenar aleatoriamente los resultados

        result = query.first()  # Obtener el primer resultado

        return result

    def deleteActividadesDeAgenda(self, idActividad, idAgenda):
        self.db_session.query(ActividadAgenda).\
            filter(ActividadAgenda.id_agenda == idAgenda,
                ActividadAgenda.id_actividad == idActividad).delete()

        self.db_session.commit()

    def getAgendasDeViaje(self, idViaje):
        agendasDiarias = self.db_session.query(AgendaDiaria).\
            join(AgendaViaje, AgendaViaje.id == AgendaDiaria.id_agenda_viaje).\
            filter(AgendaViaje.id == idViaje).all()
        
        return agendasDiarias

    def getAgendaDiaria(self, id):
        agenda = self.db_session.query(
            AgendaDiaria.id,
            ActividadAgenda.horadesde,
            ActividadAgenda.horahasta,

            Actividad.id,
            Actividad.nombre,
            Lugar.id,
            Lugar.nombre,

            Ciudad.id
            
        ).select_from(AgendaDiaria).\
        join(ActividadAgenda, AgendaDiaria.id == ActividadAgenda.id_agenda).\
        join(Actividad, ActividadAgenda.id_actividad == Actividad.id).\
        join(ActividadLugar, Actividad.id == ActividadLugar.id_actividad).\
        join(Lugar, ActividadLugar.id_lugar == Lugar.id).\
        outerjoin(Ciudad, Lugar.id_ciudad == Ciudad.id).\
        filter(AgendaDiaria.id == id).\
            order_by(ActividadAgenda.horadesde).all()

        return agenda
    
    def getActividadAgendaDiaria(self, id_agendadiaria, id_actividad):
        actividad_agenda = self.db_session.query(ActividadAgenda).\
                filter(ActividadAgenda.id_agenda == id_agendadiaria).\
                filter(ActividadAgenda.id_actividad == id_actividad).first()
         
        return actividad_agenda