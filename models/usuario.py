from tkinter import Image
from sqlalchemy import Integer
from sqlalchemy.ext.declarative import declarative_base
from ..bd.conexion import getEngine
import sqlalchemy as db

#base = declarative_base()
metadata_obj = db.MetaData()

class usuario():
   usuarios = db.Table(
      'usuarios',
      metadata_obj,
      db.Column('id',Integer, primary_key=True),
      db.Column('nombre',db.String),
      db.Column('gmail',db.String),
      db.Column('contraseña',db.String),
      )
   
   metadata_obj.create_all(getEngine())