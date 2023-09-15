from sqlalchemy import Column, Integer, PrimaryKeyConstraint, String, true
from sqlalchemy.ext.declarative import declarative_base
from ..bd.conexion import getEngine, Base
import sqlalchemy as db

metadata_obj = db.MetaData()

class LugarCategoria(Base):
    __tablename__ = 'lugares_categorias'
    id_lugar = Column(db.ForeignKey("lugares.id"), primary_key=true)
    id_categoria = Column(db.ForeignKey("categorias.id"), primary_key=true)
    
    metadata_obj.create_all(getEngine())

    def to_dict(self):
      return { 
        "id_lugar": self.id_lugar,
        "id_categoria": self.id_categoria
      }