from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from ..bd.conexion import getEngine, Base
import sqlalchemy as db

metadata_obj = db.MetaData()

class Actividad(Base):
   __tablename__ = 'actividades_agenda'
   id = Column(Integer, primary_key=True)
   nombre = Column(String)
   horaDesde = Column(String)
   horaHasta = Column(String)
   dia_viaje_id = Column(db.ForeignKey("dias_viajes.id"))
  
   metadata_obj.create_all(getEngine())

   def to_dict(self):
      return {
        "id": self.id,
        "nombre": self.horaDesde,
        "horaDesde": self.horaDesde,
        "horaHasta": self.horaHasta,
      }