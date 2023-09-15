from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from ..bd.conexion import getEngine, Base
import sqlalchemy as db

metadata_obj = db.MetaData()

class Actividad(Base):
   __tablename__ = 'actividades'
   id = Column(Integer, primary_key=True)
   nombre = Column(String)
   horaInicio = Column(String)
   horaFin = Column(String)
   valoracion = Column(Integer)
   id_agenda_diaria = Column(db.ForeignKey("agendas_diarias.id"))
   id_lugar = Column(db.ForeignKey("lugares.id"))
  
   metadata_obj.create_all(getEngine())

   def to_dict(self):
      return {
        "id": self.id,
        "nombre": self.nombre,
        "horaInicio": self.horaInicio,
        "horaFin": self.horaFin,
        "valoracion": self.valoracion,
        "id_agenda_diaria": self.id_agenda_diaria,
      }