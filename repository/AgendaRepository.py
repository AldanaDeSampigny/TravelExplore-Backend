from ..models.meGusta import meGustas
from ..models.agenda import Agenda
from sqlalchemy.orm import sessionmaker
from ..models.usuario import usuarios
from ..models.viaje import viajes

class AgendaRepository:
    def __init__(self, db_session): #esto seria un constructor
        self.db_session = db_session

    def crear_agenda(self, horaInicio, horaFin): 
        agenda = agenda(hora_inicio= horaInicio, hora_fin= horaFin)
        self.db_session.add(agenda)
        self.db_session.commit()
        return agenda

    def buscarGustos(self, usuarioID, viajeID):
        print(usuarioID, viajeID,"llego")
        # Consulta SQL utilizando SQLAlchemy
        query = self.db_session.query(meGustas.id).\
            join(viajes, meGustas.viaje_id == viajes.id).\
            join(usuarios, viajes.usuario_id == usuarios.id).\
            filter(usuarios.id == usuarioID).\
            filter(viajes.id == viajeID)

        # Ejecutar la consulta y obtener los resultados
        gustos = query.all()
        #print(gustos)

        # Retornar los resultados como una lista de IDs de gustos
        return gustos
        