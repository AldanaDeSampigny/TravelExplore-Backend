from sqlalchemy import Column, Integer, PrimaryKeyConstraint, String, Time, true,false
from sqlalchemy.ext.declarative import declarative_base
from ..bd.conexion import getEngine, Base
import sqlalchemy as db

metadata_obj = db.MetaData()

class ActividadAgenda(Base):
    __tablename__ = 'actividades_agendas'
    id_agenda = Column(db.ForeignKey("agendas_diarias.id"), primary_key= True)
    id_actividad = Column(db.ForeignKey("actividades.id"), primary_key= True)
    horadesde = Column(Time)
    horahasta = Column(Time)
    
    metadata_obj.create_all(getEngine())

    def to_dict(self):
      return { 
        "id_agenda": self.id_agenda,
        "id_actividad": self.id_actividad,
        "horadesde": self.horadesde,
        "horahasta": self.horahasta
      }