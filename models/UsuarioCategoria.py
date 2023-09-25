from sqlalchemy import Column, Integer, PrimaryKeyConstraint, String, true
from sqlalchemy.ext.declarative import declarative_base
from ..bd.conexion import getEngine, Base
import sqlalchemy as db

metadata_obj = db.MetaData()

class UsuarioCategoria(Base):
    __tablename__ = 'usuarios_categorias'
    id_usuario = Column(db.ForeignKey("usuarios.id"), primary_key=True)
    id_categorias = Column(db.ForeignKey("categorias.id"), primary_key=True)
    
    metadata_obj.create_all(getEngine())

    def to_dict(self):
      return { 
        "id_usuario": self.id_usuario,
        "id_categorias": self.id_categorias
      }