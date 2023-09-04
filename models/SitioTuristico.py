from tkinter import Image
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from ..bd.conexion import getEngine
import sqlalchemy as db

#base = declarative_base()
metadata_obj = db.MetaData()

class SitioTuristico():
   profile = db.Table(
      'sitios_turisticos',
      metadata_obj,
      db.Column('id',Integer, primary_key=True),
      db.Column('imagen',db.String),
      db.Column('nombre',db.String),
      db.Column('descripcion',db.String),
      db.Column('valoracion',db.Integer),
      db.Column('horarioApertura',db.Time),
      db.Column('horarioCierre',db.Time),
   ) 
   
   metadata_obj.create_all(getEngine())
