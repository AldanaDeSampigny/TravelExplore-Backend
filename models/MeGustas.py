from sqlalchemy import ForeignKey, create_engine, Column, Integer, String, Time
from sqlalchemy.ext.declarative import declarative_base
from ..bd.conexion import getEngine, Base
import sqlalchemy as db

#base = declarative_base()
metadata_obj = db.MetaData()

class MeGustas(Base):
    __tablename__ = 'meGustas'

    id = Column(Integer, primary_key=True)
    imagen = Column(String)
    nombre = Column(String)
    descripcion = Column(String)
    tipo = Column(String)
    valoracion = Column(Integer)
    horarioApertura = Column(Time)
    horarioCierre = Column(Time)
    direccion = Column(String)
    duracion = Column(Time)
    viaje_id = Column(Integer, ForeignKey('viajes.id'))
    agenda_id = Column(Integer, ForeignKey('agendas.id'))

    metadata_obj.create_all(getEngine())

    def to_dict(self):
      return {
        "id": self.id,
        "nombre": self.nombre,
        "descripcion": self.descripcion,
        "tipo": self.tipo,
        "valoracion": self.valoracion,
        "horarioApertura": self.horarioApertura,
        "horarioCierre": self.horarioCierre,
        "direccion": self.direccion,
        "duracion": self.duracion,
        "viaje_id": self.viaje_id,
        "agenda_id": self.agenda_id
      }