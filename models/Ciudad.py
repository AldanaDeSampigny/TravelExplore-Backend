from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from ..bd.conexion import getEngine, Base
import sqlalchemy as db

metadata_obj = db.MetaData()

class Ciudad(Base):
   __tablename__ = 'ciudades'
   id = Column(Integer, primary_key=True)
   nombre = Column(String)
   codigo = Column(String)
   latitud = Column(Float)
   longitud = Column(Float)
   #id_provincia = Column(db.ForeignKey("provincias.id"))
   
   metadata_obj.create_all(getEngine())

   def to_dict(self):
      return {
        "id": self.id,
        "nombre": self.nombre,
        "codigo": self.codigo,
        "latitud": self.latitud,
        "longitud": self.longitud
      }