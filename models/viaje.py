from tkinter import Image
from sqlalchemy import DATE, Column, Date, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from ..bd.conexion import getEngine, Base
import sqlalchemy as db

#base = declarative_base()
metadata_obj = db.MetaData()

class viajes(Base):
    __tablename__ = 'viajes'
    id = Column(Integer, primary_key=True)
    fechaDesde = Column(DATE)
    fechaHasta = Column(Date)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    destino_id = Column(Integer, ForeignKey('destinos.id'))
   
    metadata_obj.create_all(getEngine())