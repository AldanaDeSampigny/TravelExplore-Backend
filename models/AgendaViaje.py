import time
from sqlalchemy import Column, Integer, String, Time
from sqlalchemy.ext.declarative import declarative_base
from ..bd.conexion import getEngine, Base
import sqlalchemy as db

metadata_obj = db.MetaData()

class AgendaViaje(Base):
    __tablename__ = 'agendas_viajes'
    id = Column(Integer, primary_key=True)
  
    def to_dict(self):
      return {
        "id": self.id
      }