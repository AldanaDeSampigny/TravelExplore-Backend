from ..models.Ciudad import Ciudad

class CiudadRepository:
    def __init__(self, db_session): #esto seria un constructor
        self.db_session = db_session

    def getCiudades(self):
        ciudades = self.db_session.query(Ciudad).all()

        return ciudades