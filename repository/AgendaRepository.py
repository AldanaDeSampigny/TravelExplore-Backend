#from requests import Session
from sqlalchemy.orm import Session
from ..models.MeGustas import MeGustas
from ..models.Agendas import Agendas
from sqlalchemy.orm import sessionmaker
from ..models.Usuarios import Usuarios
from ..models.Viajes import Viajes
from sqlalchemy import func

class AgendaRepository:
    def __init__(self, db_session): #esto seria un constructor
        self.db_session = db_session

    def crear_agenda(self, horaInicio, horaFin): 
        agenda = agenda(hora_inicio= horaInicio, hora_fin= horaFin)
        self.db_session.add(agenda)
        self.db_session.commit()
        return agenda

    def buscarGustosPersonalizado(self, usuarioID, viajeID):
        session = Session(self.db_session)
        print(usuarioID, viajeID,"llego")

        result = session.query(MeGustas)\
            .join(Viajes)\
            .join(Usuarios)\
            .filter(Viajes.id == viajeID)\
            .filter(Usuarios.id == usuarioID)\
            .all()
        
        return result
    
# Consulta SQL utilizando SQLAlchemy
    def buscarGustos(self, usuarioID, viajeID):
        query = self.db_session.query(MeGustas.id).\
            join(Viajes, MeGustas.viaje_id == Viajes.id).\
            join(Usuarios, Viajes.usuario_id == Usuarios.id).\
            filter(Usuarios.id == usuarioID).\
            filter(Viajes.id == viajeID)

        query = query.order_by(func.random())
        gustos = query.all()
        return gustos        