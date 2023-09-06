from tkinter import Image
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from ..bd.conexion import getEngine
import sqlalchemy as db

#base = declarative_base()
metadata_obj = db.MetaData()

class viajes():
   profile = db.Table(
      'viajes',
      metadata_obj,
      db.Column('id',Integer, primary_key=True),
      db.Column('nombre',db.String),
      db.column('fechaDesde', db.Date),
      db.column('fechaHasta', db.Date),
      db.column('usuario_id', db.Integer, ForeignKey('usuarios.id')),
      db.column('destino_id', db.Integer, ForeignKey('destinos.id'))
      )
   
   metadata_obj.create_all(getEngine())