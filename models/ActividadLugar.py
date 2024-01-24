from sqlalchemy import Column, Time
from ..bd.conexion import getEngine, Base
import sqlalchemy as db

metadata_obj = db.MetaData()


class ActividadLugar(Base):
    __tablename__ = 'actividades_lugares'
    id_lugar = Column(db.ForeignKey("lugares.id"), primary_key=True)
    id_actividad = Column(db.ForeignKey("actividades.id"), primary_key=True)

    metadata_obj.create_all(getEngine())

    def to_dict(self):
      return {
          "id_lugar": self.id_lugar,
          "id_actividad": self.id_actividad
      }
