from ast import List
from sqlalchemy import Column, Integer, String, false
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
  id_ciudad = Column(db.ForeignKey("ciudades.id"))
  #categorias = relationship('Categoria', secondary='lugares_categorias', back_populates='lugares')


  metadata_obj.create_all(getEngine())

  def to_dict(self):
    return {
      "id": self.id,
      "nombre": self.nombre,
      "codigo": self.codigo,
    }