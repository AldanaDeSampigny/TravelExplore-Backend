from tkinter import Image
from sqlalchemy import Boolean, ForeignKey,table, create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from ..bd.conexion import getEngine
import sqlalchemy as db
from sqlalchemy.orm import relationship

#base = declarative_base()
metadata_obj = db.MetaData()

class Agenda():
   profile = db.Table(
      'agendas',
      metadata_obj,
      db.Column('id',Integer, primary_key=True),
      db.Column('horaInicio',db.TIMESTAMP),
      db.Column('horaFin',db.TIMESTAMP),
      sitios_turisticos = relationship("SitioTuristico", secondary="agenda_sitio_turistico")

   ) 
   
   metadata_obj.create_all(getEngine())
