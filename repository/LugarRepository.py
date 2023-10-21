from ..models.Provincia import Provincia
from ..models.Pais import Pais
from ..models.Ciudad import Ciudad
from ..models.Lugar import Lugar
from sqlalchemy.orm import sessionmaker

class LugarRepository:
    def __init__(self, db_session): #esto seria un constructor
        self.db_session = db_session

    def getLugares(self):
        lugares = self.db_session.query(Lugar).all()

        return lugares

    def getLugar(self, codigoLugar):
        lugar = self.db_session.query(Lugar).\
            filter(Lugar.codigo == codigoLugar).first()

        return lugar
    
    def getCiudad(self, codigoCiudad, nombreCiudad):
        ciudad = self.db_session.query(Ciudad).\
            filter((Ciudad.codigo == codigoCiudad) |(Ciudad.codigo.is_(None))).\
            filter(Ciudad.nombre == nombreCiudad).first()

        return ciudad
    
    def getProvincia(self, codigoProvincia, nombreProvincia):
        provincia = self.db_session.query(Provincia).\
            filter((Provincia.codigo == codigoProvincia) | (Provincia.codigo.is_(None))).\
            filter(Provincia.nombre == nombreProvincia).first()

        return provincia
    
    def getPais(self, codigoPais, nombrePais):
        pais = self.db_session.query(Pais).\
            filter((Pais.codigo == codigoPais) | (Pais.codigo.is_(None))).\
            filter(Pais.nombre == nombrePais).first()

        return pais
    
    def getCiudadLugar(self, nombreCiudad):
        ciudad = self.db_session.query(Ciudad).\
            join(Provincia, Provincia.id == Ciudad.id_provincia).\
            join(Pais, Pais.id == Provincia.id_pais).\
            filter(Ciudad.nombre == nombreCiudad).first()
        
        return ciudad
    
    def getProvinciaCiudad(self, nombreProvincia):
        provincia = self.db_session.query(Provincia).\
            join(Pais, Pais.id == Provincia.id_pais).\
            filter(Provincia.nombre == nombreProvincia).first()
        
        return provincia
        
    def getPaisProvincia(self, nombrePais):
        pais = self.db_session.query(Pais).\
            filter(Pais.nombre == nombrePais).first()
        
        return pais
