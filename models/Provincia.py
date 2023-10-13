from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from ..bd.conexion import getEngine, Base
import sqlalchemy as db

metadata_obj = db.MetaData()

class Provincia(Base):
   __tablename__ = 'provincias'
   id = Column(Integer, primary_key=True)
   nombre = Column(String)
   id_pais = Column(db.ForeignKey("paises.id"))
   
   metadata_obj.create_all(getEngine())

   def to_dict(self):
      return {
        "id": self.id,
        "nombre": self.nombre,
      }