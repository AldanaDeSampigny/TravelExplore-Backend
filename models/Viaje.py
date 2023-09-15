from sqlalchemy import Column, Date, ForeignKey, Integer,String
from sqlalchemy.ext.declarative import declarative_base
from ..bd.conexion import getEngine, Base
import sqlalchemy as db
from sqlalchemy.orm import relationship

metadata_obj = db.MetaData()

class Viaje(Base):
  __tablename__ = 'viajes'
  id = Column(Integer, primary_key=True)
  fechaDesde = Column(Date)
  fechaHasta = Column(Date)
  id_usuario = Column(db.ForeignKey("usuarios.id"))
  #agenda = Column(db.ForeignKey("agendas.id"))
  
  metadata_obj.create_all(getEngine())

  def to_dict(self):
    return {
      "id": self.id,
      "fechaDesde": self.fechaDesde,
      "fechaHasta": self.fechaHasta,
      "id_usuario": self.id_usuario
    }