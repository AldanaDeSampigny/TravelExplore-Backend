from tkinter import Image
from sqlalchemy import Date,Boolean, ForeignKey, Time,table, create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from ..bd.conexion import getEngine, Base
import sqlalchemy as db
from sqlalchemy.orm import relationship

#base = declarative_base()
metadata_obj = db.MetaData()

class Agendas(Base):
   __tablename__ = 'agendas'
   id = Column(Integer, primary_key=True)
   horaInicio = Column(Time)
   horaInicioFin = Column(Time)
   destino_id = Column(Integer,ForeignKey('destinos.id'))

   metadata_obj.create_all(getEngine())

   def to_dict(self):
      return {
         "id": self.id,
         "horaInicio": self.horaInicio,
         "horaFin": self.horaFin,
      }