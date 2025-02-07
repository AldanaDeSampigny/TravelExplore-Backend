from ..models.ActividadLugar import ActividadLugar
from ..models.ActividadesFavoritas import ActividadesFavoritas
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
        actividades = self.db_session.query(Actividad).all()

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
    
    def getLugaresDeActividad(self,idActividad,idCiudad):
        lugares = self.db_session.query(                                
            Actividad.id,
            Lugar.id,
            Lugar.nombre,
        ).join(ActividadLugar, Actividad.id == ActividadLugar.id_actividad).\
        join(Lugar, ActividadLugar.id_lugar == Lugar.id).\
        join(Ciudad, Lugar.id_ciudad == Ciudad.id).\
        filter(Actividad.id == idActividad).\
        filter(Ciudad.id == idCiudad)

        return lugares
    
    def getActividadesOdiadas(self, usuarioID):
        actividades = self.db_session.query(ActividadesFavoritas.actividad_id).\
            filter(ActividadesFavoritas.usuario_id == usuarioID).\
            filter(ActividadesFavoritas.like == 0).all()
        
        return [row[0] for row in actividades]
    
    def getActividadesFavoritas(self, usuarioID):
        actividades = self.db_session.query(ActividadesFavoritas.actividad_id).\
            filter(ActividadesFavoritas.usuario_id == usuarioID).\
            filter(ActividadesFavoritas.like == 1).all()
        
        return [row[0] for row in actividades]
