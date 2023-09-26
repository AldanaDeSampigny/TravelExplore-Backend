from tkinter import Image
from sqlalchemy import Date,Boolean, ForeignKey, Time,table, create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from ..bd.conexion import getEngine, Base
import sqlalchemy as db
from sqlalchemy.orm import relationship

#base = declarative_base()
metadata_obj = db.MetaData()

class AgendaDiaria(Base):
   __tablename__ = 'agendas_diarias'
   id = Column(Integer, primary_key=True)
   horaInicio = Column(Time)
   horaFin = Column(Time)
   dia = Column(Date)
   itinerario_id = Column(db.ForeignKey("itinerarios.id"))
   id_agenda_viaje = Column(db.ForeignKey("agendas_viajes.id"))

   metadata_obj.create_all(getEngine())

   def to_dict(self):
      return {
         "id": self.id,
         "horaInicio": self.horaInicio,
         "horaFin": self.horaFin,
         "dia": self.dia,
         "itinerario": self.itinerario_id,
         "id_agenda_viaje": self.id_agenda_viaje
      }