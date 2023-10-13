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