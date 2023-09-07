from tkinter import Image
from sqlalchemy import Boolean, ForeignKey, Time,table, create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from ..bd.conexion import getEngine, Base
import sqlalchemy as db
from sqlalchemy.orm import relationship

#base = declarative_base()
metadata_obj = db.MetaData()

class Agenda(Base):
   __tablename__ = 'agendas'
   id = Column(Integer, primary_key=True)
   horaInicio = Column(Time)
   horaFin = Column(Time)
   
   metadata_obj.create_all(getEngine())