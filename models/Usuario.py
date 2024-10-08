from tkinter import Image
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from ..bd.conexion import getEngine, Base
import sqlalchemy as db

metadata_obj = db.MetaData()

class Usuario(Base):
   __tablename__ = 'usuarios'
   id = Column(Integer, primary_key=True)
   nombre = Column(String)
   gmail = Column(String)
   contrasenia = Column(String)
   admin = Column(Boolean)
   imagen = Column(String)
   token = Column(String)
   
   metadata_obj.create_all(getEngine())

   def to_dict(self):
      return {
         "id": self.id,
         "nombre": self.nombre,
         "gmail": self.gmail,
         "contrasenia": self.contrasenia,
         "admin": self.admin,
         "imagen": self.imagen,
         "token": self.token
      }