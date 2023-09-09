from sqlalchemy import Column, Date, ForeignKey, Integer,String
from sqlalchemy.ext.declarative import declarative_base
from ..bd.conexion import getEngine, Base
import sqlalchemy as db
from sqlalchemy.orm import relationship

metadata_obj = db.MetaData()

class DiaViaje(Base):
  __tablename__ = 'dias_viajes'
  id = Column(Integer, primary_key=True)
  fecha = Column(String)
  viaje = Column(db.ForeignKey("viajes.id"))

  metadata_obj.create_all(getEngine())

  def to_dict(self):
    return {
      "id": self.id,
      "horaDesde": self.horaDesde,
      "horaHasta": self.horaHasta,
    }