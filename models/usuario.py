from tkinter import Image
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from ..bd.conexion import getEngine, Base
import sqlalchemy as db

#base = declarative_base()
metadata_obj = db.MetaData()

class usuario(Base):
   __tablename__ = 'usuarios'
   id = Column(Integer, primary_key=True)
   nombre = Column(String)
   gmail = Column(String)
   contraseña = Column(String)
   
   metadata_obj.create_all(getEngine())