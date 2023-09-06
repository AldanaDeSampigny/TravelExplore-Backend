from models.meGusta import SitioTuristico
from sqlalchemy.orm import sessionmaker

class meGustaRepository:
    def __init__(self, db_session): #esto seria un constructor
        self.db_session = db_session

#este metodo seria para añdir/guardar una nueva actividad
    def crear_sitio(self, nombre, hora_inicio, hora_fin): 
        actividad = Actividad(nombre=nombre, hora_inicio=hora_inicio, hora_fin=hora_fin)
        self.db_session.add(actividad)
        self.db_session.commit()
        return actividad

