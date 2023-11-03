from sqlalchemy import Column, Integer, PrimaryKeyConstraint, String, true
from sqlalchemy.ext.declarative import declarative_base
from ..bd.conexion import getEngine, Base
import sqlalchemy as db

metadata_obj = db.MetaData()


class CiudadCategoria(Base):
    __tablename__ = 'ciudades_categorias'
    id_ciudad = Column(db.ForeignKey("ciudades.id"), primary_key=True)
    id_categoria = Column(db.ForeignKey("categorias.id"), primary_key=True)

    metadata_obj.create_all(getEngine())

    def to_dict(self):
        return {
            "id_ciudad": self.id_ciudad,
            "id_categoria": self.id_categoria
        }
