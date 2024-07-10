from tkinter import Image
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from ..bd.conexion import getEngine, Base
import sqlalchemy as db

metadata_obj = db.MetaData()

class Reseña(Base):
   __tablename__ = 'resenias'
   id = Column(Integer, primary_key=True)
   resenia = Column(String)
   id_lugar = Column(db.ForeignKey("lugares.id"))
   id_usuario = Column(db.ForeignKey("usuarios.id"))
   
   metadata_obj.create_all(getEngine())

   def to_dict(self):
      return {
         "id": self.id,
         "resenia": self.resenia,
         "id_lugar": self.id_lugar,   
         "id_usuario": self.id_usuario,   
        
      }