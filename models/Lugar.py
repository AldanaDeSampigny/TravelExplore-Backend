from ast import List
from sqlalchemy import Column, Float, Integer, String, Time, false
from sqlalchemy.ext.declarative import declarative_base
from ..bd.conexion import getEngine, Base
import sqlalchemy as db
from sqlalchemy.orm import relationship
metadata_obj = db.MetaData()

class Lugar(Base):
  __tablename__ = 'lugares'
  id = Column(Integer, primary_key=True) 
  codigo = Column(String)
  nombre = Column(String)
  tipo = Column(String)
  latitud = Column(Float) 
  longitud = Column(Float)
  imagen = Column(String)
  valoracion = Column(Float)
  horaapertura = Column(Time)  
  horacierre = Column(Time)
  id_ciudad = Column(db.ForeignKey("ciudades.id"))
  valoracion_usuario = Column(Integer)

  #categorias = relationship('Categoria', secondary='lugares_categorias', back_populates='lugares')


  metadata_obj.create_all(getEngine())

  def to_dict(self):
    return {
      "id": self.id,
      "nombre": self.nombre,
      "codigo": self.codigo,
      "tipo": self.tipo,
      "latitud": self.latitud,
      "longitud": self.longitud,
      "valoracion": self.valoracion,
      "horaapertura": self.horaapertura,
      "horacierre": self.horacierre,
      "valoracion_usuario": self.valoracion_usuario
    }