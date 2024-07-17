import datetime
import re
from turtle import update
import json

from ..repository.AgendaRepository import AgendaRepository

from ..models.Lugar import Lugar
from ..repository.LugarRepository import LugarRepository

from ..bd.conexion import getEngine
from sqlalchemy.orm import Session


class ActividadesService:
    def __init__(self, db_session):
        self.db_session = db_session

    def obtenerLugarActividad(self, idActividad):
        with Session(getEngine()) as session:
            lugarRepo = LugarRepository(session)
            lugares = lugarRepo.buscarLugaresRecomendacion(idActividad)
            print("lugares" ,lugares)
            if lugares == []:
                return None
            else:
                return lugares[0]

