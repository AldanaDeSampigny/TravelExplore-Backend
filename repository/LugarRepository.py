from ..models.Provincia import Provincia
from ..models.Pais import Pais
from ..models.Ciudad import Ciudad
from ..models.ActividadCategoria import ActividadCategoria
from ..models.Actividad import Actividad
from ..models.Categoria import Categoria
from ..models.Lugar import Lugar
from sqlalchemy.orm import sessionmaker

class ActividadRepository:
    def __init__(self, db_session): #esto seria un constructor
        self.db_session = db_session

    def getLugar(self, idLugar):
        lugar = self.db_session.query(Lugar).\
            filter(Lugar.id == idLugar).first()

        return lugar
    
    def getProveniencia(self, codigo):
        proveniente = self.db_session.query(Pais.nombre, Provincia.nombre, Ciudad.nombre).\
        join(Ciudad, Ciudad.id == Lugar.id_ciudad).\
        join(Provincia, Provincia.id == Ciudad.id_provincia).\
        join(Pais, Pais.id == Provincia.id_pais).\
        filter(Lugar.codigo == codigo)
        