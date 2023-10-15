from sqlalchemy import Column, Date, ForeignKey, Integer,String
from sqlalchemy.ext.declarative import declarative_base
from ..bd.conexion import getEngine, Base
import sqlalchemy as db
from sqlalchemy.orm import relationship

metadata_obj = db.MetaData()

class LugaresFavoritos(Base):
    __tablename__ = 'lugares_favoritos'
    lugar_id = Column(Integer, ForeignKey('lugares.id'), primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'),  primary_key=True)

    metadata_obj.create_all(getEngine())

    def to_dict(self):
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "lugar_id": self.actividad_id
        }


