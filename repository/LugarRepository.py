from ..models.Usuario import Usuario
from ..models.Horario import Horario
from ..models.CiudadCategoria import CiudadCategoria
from ..models.LugarCategoria import LugarCategoria
from ..models.Ciudad import Ciudad
from ..models.Lugar import Lugar
from ..models.Reseña import Reseña
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

    def getLugarID(self, lugarID):
        lugar = self.db_session.query(Lugar).\
            filter(Lugar.id == lugarID).first()

        return lugar
    
    def getLugarCategoria(self, idLugar):
        lugar = self.db_session.query(LugarCategoria).\
            filter(LugarCategoria.id_lugar == idLugar).first()

        return lugar
    
    def getCiudadCategoria(self, idCiudad):
        ciudad = self.db_session.query(CiudadCategoria).\
            filter(CiudadCategoria.id_ciudad == idCiudad).first()

        return ciudad
    
    def getLugarById(self, id):
        lugar = self.db_session.query(Lugar).\
            filter(Lugar.codigo == id).first()

        return lugar
    
    def getCiudad(self, codigoCiudad):
        ciudad = self.db_session.query(Ciudad).\
            filter((Ciudad.codigo == codigoCiudad)).first()

        return ciudad
    
    def getCiudadLugar(self, nombreCiudad):
        ciudad = self.db_session.query(Ciudad).\
            filter(Ciudad.nombre == nombreCiudad).first()
        
        return ciudad
    
    def getLugarHorario(self, idlugar):
        horario = self.db_session.query(Horario.dia, Horario.horaInicio, Horario.horaFin).\
            filter(Horario.id_lugar == idlugar).all()

        return horario

    def agregarValoracionUsuario(self, id, valoracion):
        lugarConValoracion = self.getLugarById(id)
        if lugarConValoracion:
            lugarConValoracion.valoracion_usuario = valoracion
            self.db_session.add(lugarConValoracion)
            self.db_session.commit()
        return lugarConValoracion

    def agregarReseña(self, lugarID, resenia,idUsuario):
        lugar = self.getLugarById(lugarID)
        
        if lugar is not None:
            nueva_resenia = Reseña(resenia=resenia, id_lugar=lugar.id,id_usuario=idUsuario)
            self.db_session.add(nueva_resenia)
            self.db_session.commit()
        else:
            raise ValueError("Lugar no encontrado")
        
        return nueva_resenia

    def ultimasReseñas(self,lugarID):
        lugar = self.getLugarById(lugarID)

        obtenerResenias = (
                self.db_session.query(Lugar.id, Reseña.resenia,Usuario.nombre,Usuario.imagen)
                .join(Reseña, Lugar.id == Reseña.id_lugar)
                .join(Usuario, Usuario.id == Reseña.id_usuario)
                .filter(Reseña.id_lugar == lugar.id)
                .order_by(Reseña.id.desc())
                .limit(3)
            )

        return obtenerResenias.all()
    
    def getValoracionUsuario(self, codigoLugar):
        valoracionUsuario = self.db_session.query(Lugar.valoracion_usuario).\
            filter(Lugar.codigo == codigoLugar).first()

        return valoracionUsuario