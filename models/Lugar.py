from ast import List
from sqlalchemy import Column, Float, Integer, String, Time, false
from sqlalchemy.ext.declarative import declarative_base
from ..bd.conexion import getEngine, Base
import sqlalchemy as db
from sqlalchemy.orm import relationship
metadata_obj = db.MetaData()

class Lugar(Base):
  __tablename__ = 'lugares'
  id = Column(Integer, primary_key=false) #el lugar puede ser nulo  
  codigo = Column(String)
  nombre = Column(String)
  horaApertura = Column(Time)
  horaCierre = Column(Time)
  tipo = Column(String)
  latitud = Column(Float) 
  longitud = Column(Float)
  id_ciudad = Column(db.ForeignKey("ciudades.id"))
  #categorias = relationship('Categoria', secondary='lugares_categorias', back_populates='lugares')


  metadata_obj.create_all(getEngine())

  def to_dict(self):
    return {
      "id": self.id,
      "nombre": self.nombre,
      "codigo": self.codigo,
      "horaApertura": self.horaApertura,
      "horaCierre": self.horaCierre,
      "tipo": self.tipo,
      "latitud": self.latitud,
      "longitud": self.longitud
    }