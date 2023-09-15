#from requests import Session
from sqlalchemy.orm import Session

from ..models.Destinos import Destinos
from ..models.MeGustas import MeGustas
from sqlalchemy.orm import sessionmaker
from ..models.Usuario import Usuarios
from sqlalchemy import func

class AgendaRepository:
    def __init__(self, db_session): #esto seria un constructor
        self.db_session = db_session

    def crear_agenda(self, horaInicio, horaFin): 
        agenda = agenda(hora_inicio= horaInicio, hora_fin= horaFin)
        self.db_session.add(agenda)
        self.db_session.commit()
        return agenda

    def buscarGustosPersonalizado(self, usuarioID, destinosID):
        session = Session(self.db_session)
        print(usuarioID, destinosID,"llego")

        result = session.query(MeGustas)\
            .join(Destinos)\
            .join(Usuarios)\
            .filter(Destinos.id == destinosID)\
            .filter(Usuarios.id == usuarioID)\
            .all()
        
        return result
    
# Consulta SQL utilizando SQLAlchemy
    def buscarGustos(self, usuarioID, destinoID):
        query = self.db_session.query(MeGustas.id).\
            join(Destinos, MeGustas.destino_id == Destinos.id).\
            join(Usuarios, MeGustas.usuario_id == Usuarios.id).\
            filter(Usuarios.id == usuarioID).\
            filter(Destinos.id == destinoID)

        query = query.order_by(func.random())
        gustos = query.all()
        return gustos        