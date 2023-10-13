from sqlalchemy import Column, Date, ForeignKey, Integer,String
from sqlalchemy.ext.declarative import declarative_base
from ..bd.conexion import getEngine, Base
import sqlalchemy as db
from sqlalchemy.orm import relationship

metadata_obj = db.MetaData()

#!BORRA TABLA DE LA BASE DE DATOS
class ActividadesFavoritas(Base):
    __tablename__ = 'actividades_favoritas'
    actividad_id = Column(Integer, ForeignKey('actividades.id'), primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'),  primary_key=True)

    metadata_obj.create_all(getEngine())

    def to_dict(self):
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "actividad_id": self.actividad_id
        }


