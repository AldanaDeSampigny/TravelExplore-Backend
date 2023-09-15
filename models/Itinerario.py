from sqlalchemy import Column, Date, ForeignKey, Integer,String
from sqlalchemy.ext.declarative import declarative_base
from ..bd.conexion import getEngine, Base
import sqlalchemy as db
from sqlalchemy.orm import relationship

metadata_obj = db.MetaData()

class Itinario(Base):
  __tablename__ = 'itinerarios'
  id = Column(Integer, primary_key=True)
  fechaDesde = Column(Date)
  fechaHasta = Column(Date)
  id_viaje = Column(db.ForeignKey("viajes.id"))
  id_ciudades = Column(db.ForeignKey("ciudades.id"))
  
  metadata_obj.create_all(getEngine())

  def to_dict(self):
    return {
      "id": self.id,
      "fechaDesde": self.fechaDesde,
      "fechaHasta": self.fechaHasta,
      "id_viaje": self.id_viaje,
      "id_ciudad": self.id_ciudad
    }