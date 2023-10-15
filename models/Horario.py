from sqlalchemy import Column, Integer, String, Time, false
from ..bd.conexion import getEngine, Base
import sqlalchemy as db
metadata_obj = db.MetaData()

class Horario(Base): 
  __tablename__ = 'horarios'
  id = Column(Integer, primary_key=false) 
  dia = Column(String)
  horaInicio = Column(Time)
  horaFin = Column(Time)
  id_lugar = Column(db.ForeignKey("lugares.id"))


  metadata_obj.create_all(getEngine())

  def to_dict(self):
    return {
      "id": self.id,
      "dia": self.dia,
      "horaInicio": self.horaInicio,
      "horaFin": self.horaFin,
    }