import time
from sqlalchemy import Column, Integer, String, Time
from sqlalchemy.ext.declarative import declarative_base
from ..bd.conexion import getEngine, Base
import sqlalchemy as db

metadata_obj = db.MetaData()

class Actividad(Base):
  __tablename__ = 'actividades'
  id = Column(Integer, primary_key=True)
  nombre = Column(String)
  valoracion = Column(Integer)
  duracion = Column(Time)
  horainicio= Column(Time)
  horafin= Column(Time)
  
  metadata_obj.create_all(getEngine())

  def to_dict(self):
      return {
        "id": self.id,
        "nombre": self.nombre,
        "valoracion": self.valoracion,
        "duracion": self.duracion,
        "horainicio": self.horainicio,
        "horafin": self.horafin
      }