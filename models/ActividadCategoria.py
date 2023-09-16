from sqlalchemy import Column, Integer, PrimaryKeyConstraint, String, true
from sqlalchemy.ext.declarative import declarative_base
from ..bd.conexion import getEngine, Base
import sqlalchemy as db

metadata_obj = db.MetaData()

class ActividadCategoria(Base):
    __tablename__ = 'actividades_categorias'
    id_actividad = Column(db.ForeignKey("actividades.id"), primary_key=true)
    id_categoria = Column(db.ForeignKey("categorias.id"), primary_key=true)
    
    metadata_obj.create_all(getEngine())

    def to_dict(self):
      return { 
        "id_actividad": self.id_actividad,
        "id_categorias": self.id_categoria
      }