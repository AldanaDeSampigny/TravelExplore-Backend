from tkinter import Image
from sqlalchemy import Integer
from sqlalchemy.ext.declarative import declarative_base
from ..bd.conexion import getEngine
import sqlalchemy as db

#base = declarative_base()
metadata_obj = db.MetaData()

class destino():
   profile = db.Table(
      'destinos',
      metadata_obj,
      db.Column('id',Integer, primary_key=True),
      db.Column('nombre',db.String),
      )
   
   metadata_obj.create_all(getEngine())