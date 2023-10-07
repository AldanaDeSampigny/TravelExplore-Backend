from ..models.ActividadCategoria import ActividadCategoria
from ..models.Actividad import Actividad
from ..models.Categoria import Categoria
from sqlalchemy.orm import sessionmaker

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

    def getActividadCategoria(self, categoriaID):
        actividad = self.db_session.query(Actividad.id).\
        join(Categoria, Categoria.id == ActividadCategoria.id_categorias).\
        join(Actividad, Actividad.id == ActividadCategoria.id_lugares).\
            filter(Categoria.id == categoriaID)

        return actividad