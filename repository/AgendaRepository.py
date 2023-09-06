from models.meGusta import SitioTuristico, meGusta
from models.agenda import Agenda
from sqlalchemy.orm import sessionmaker
from models.usuario import usuario

from models.viaje import viajes

class AgendaRepository:
    def __init__(self, db_session): #esto seria un constructor
        self.db_session = db_session

    def crear_agenda(self, horaInicio, horaFin): 
        agenda = agenda(hora_inicio= horaInicio, hora_fin= horaFin)
        self.db_session.add(agenda)
        self.db_session.commit()
        return agenda

#metodo para añadir sitios a una agenda
#    def agregar_sitio_turistico(self, agenda_id, sitio_turistico_id):
#       agenda = self.db_session.query(Agenda).filter_by(id=agenda_id).first()

#      if not agenda:
#         raise Exception("La agenda no existe")

#    sitio_turistico = self.db_session.query(SitioTuristico).filter_by(id=sitio_turistico_id).first()
#      if not sitio_turistico:
#           raise Exception("El sitio turístico no existe")

# Agrega el sitio turístico a la agenda solo si no está en la lista
#      if sitio_turistico not in agenda.sitios_turisticos:
#        agenda.sitios_turisticos.append(sitio_turistico)
# Guarda los cambios en la base de datos
#    self.db_session.commit()


    def buscarGustos(self, usuario_id, viaje_id):
        # Consulta SQL utilizando SQLAlchemy
        query = self.db_session.query(meGusta.id).\
            join(viajes, meGusta.viaje_id == viajes.id).\
            join(usuario, viajes.usuario_id == usuario.id).\
            filter(usuario.id == usuario_id).\
            filter(viajes.id == viaje_id)

        # Ejecutar la consulta y obtener los resultados
        gustos = query.all()

        # Retornar los resultados como una lista de IDs de gustos
        return [gusto.id for gusto in gustos]