from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from ..bd.conexion import getEngine, Base
import sqlalchemy as db

metadata_obj = db.MetaData()


class PalabrasProhibidas(Base):
   __tablename__ = 'palabras_prohibidas'
   id = Column(Integer, primary_key=True)
   palabra = Column(String)

   metadata_obj.create_all(getEngine())

   def to_dict(self):
      return {
          "id": self.id,
          "palabra": self.nombre
      }
