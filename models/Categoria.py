from ast import List
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from ..bd.conexion import getEngine, Base
import sqlalchemy as db
from sqlalchemy.orm import relationship

metadata_obj = db.MetaData()

class Categoria(Base):
    __tablename__ = 'categorias'
    id = Column(Integer, primary_key=True)
    codigo = Column(String)
    nombre = Column(String)

    metadata_obj.create_all(getEngine())

    def to_dict(self):
      return {
        "id": self.id,
        "nombre": self.nombre,
        "codigo": self.codigo,
      }