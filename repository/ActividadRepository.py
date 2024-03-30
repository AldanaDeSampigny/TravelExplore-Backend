from ..models.ActividadLugar import ActividadLugar
from ..models.ActividadCategoria import ActividadCategoria
from ..models.Actividad import Actividad
from ..models.Categoria import Categoria
from ..models.Lugar import Lugar
from ..models.Ciudad import Ciudad
from ..models.AgendaDiaria import AgendaDiaria
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

class ActividadRepository:
    def __init__(self, db_session): #esto seria un constructor
        self.db_session = db_session

    def getActividades(self):
        actividades = self.db_session.query(Actividad).\
            group_by(Actividad.id).\
            order_by(func.min(Actividad.id)).all()

        return actividades
    
    def getActividad(self, id):
        actividad = self.db_session.query(Actividad).\
            filter(Actividad.id == id).first()

        return actividad
    
    def getActividadNombre(self, nombre):
        actividad = self.db_session.query(Actividad).\
            filter(Actividad.id == id).first()
        return actividad
    
    
    def getActividadCategoria(self, categoriaID):
        actividad = self.db_session.query(Actividad.id).\
        join(Categoria, Categoria.id == ActividadCategoria.id_categorias).\
        join(Actividad, Actividad.id == ActividadCategoria.id_lugares).\
            filter(Categoria.id == categoriaID)

        return actividad

    def getActividadCategorias(self, categoriaIDs):
        subquery = self.db_session.query(ActividadCategoria.id_actividad).\
            filter(ActividadCategoria.id_categoria.in_(categoriaIDs)).\
            group_by(ActividadCategoria.id_actividad).\
            having(func.count(ActividadCategoria.id_categoria) == len(categoriaIDs)).subquery()

        actividades = self.db_session.query(Actividad).\
            join(ActividadCategoria, Actividad.id == ActividadCategoria.id_actividad).\
            filter(Actividad.id.in_(subquery))

        return actividades
    
    def getLugaresDeActividad(self, idCiudad, idActividad):
        lugares = self.db_session.query(
            Actividad.id,
            Lugar.id,
            Lugar.nombre,
        ).join(ActividadLugar, ActividadLugar.id_lugar == Lugar.id).\
        join(Actividad, Actividad.id == ActividadLugar.id_actividad).\
        join(Ciudad, Ciudad.id == Lugar.id_ciudad).\
        filter(Actividad.id == idActividad).\
        filter(Ciudad.id == idCiudad).all()

        return lugares
    """         
        def getAgendaDiaria(self, id):
        agenda = (self.db_session.query(
            AgendaDiaria.id,
            AgendaDiaria.horaInicio,
            AgendaDiaria.horaFin,

            Actividad.id,
            Lugar.id,
            Ciudad.id,
            
        ).join(ActividadAgenda, ActividadAgenda.id_agenda == AgendaDiaria.id).\
        join(Actividad, ActividadLugar.id_actividad == Actividad.id) .\
        join(Lugar, ActividadLugar.id_lugar == Lugar.id).\
        join (Ciudad, Itinenario.id_ciudad == Ciudad.id).\
        filter (Actividad.id == ActividadLugar.id_actividad).\
        filter (Lugar.id == ActividadLugar.id_lugar).\
        filter (Ciudad.id == Itinerario.id_ciudad).\
        
    ) """