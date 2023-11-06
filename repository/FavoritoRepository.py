from sqlalchemy import update

from ..models.ActividadesFavoritas import ActividadesFavoritas
from ..models.Actividad import Actividad

from ..models.Ciudad import Ciudad
from ..models.Usuario import Usuario
from ..models.Lugar import Lugar
from ..models.LugaresFavoritos import LugaresFavoritos

class FavoritoRepository:
    def __init__(self, db_session): #esto seria un constructor
        self.db_session = db_session

    def getLugarUsuario(self,idUsuario,codigoLugar):
        lugarFavoritoUsuario = self.db_session.query(
            LugaresFavoritos.lugar_id,
            LugaresFavoritos.usuario_id,
            LugaresFavoritos.like,
            Lugar.codigo).\
        join(Lugar,LugaresFavoritos.lugar_id == Lugar.id).\
        filter(LugaresFavoritos.usuario_id == idUsuario).\
        filter(Lugar.codigo == codigoLugar)

        return lugarFavoritoUsuario.first()
    
    def getLugar(self, idLugar):
        lugar = self.db_session.query(LugaresFavoritos).\
            filter(LugaresFavoritos.lugar_id == idLugar).first()

        return lugar

    def updateLike(self, usuarioId, idLugar, nuevoLike):
        nuevoLugar = self.getLugar(idLugar)
        nuevoLugar.like = nuevoLike

        self.db_session.add(nuevoLugar)
        self.db_session.commit()


    def favoritosUsuario(self, usuarioID):
        lugaresFavoritosUsuario = self.db_session.query(
            Lugar.nombre,
            Ciudad.nombre,
            Usuario.nombre,
            LugaresFavoritos.like,
            Lugar.codigo
            ).\
        join(Lugar, LugaresFavoritos.lugar_id == Lugar.id).\
        join(Usuario, LugaresFavoritos.usuario_id == Usuario.id).\
        join(Ciudad,Lugar.id_ciudad == Ciudad.id).\
        filter(Usuario.id == usuarioID).\
        filter(LugaresFavoritos.like == 1).all()

        return lugaresFavoritosUsuario
    

    def getActividadUsuario(self,idUsuario,idActividad):
        actividadFavoritaUsuario = self.db_session.query(
            ActividadesFavoritas.actividad_id,
            ActividadesFavoritas.usuario_id,
            ActividadesFavoritas.like,
            Actividad.id).\
        join(Actividad,ActividadesFavoritas.actividad_id == Actividad.id).\
        filter(ActividadesFavoritas.usuario_id == idUsuario).\
        filter(Actividad.id == idActividad)

        return actividadFavoritaUsuario.first()

    def getActividad(self, idActividad):
        actividad = self.db_session.query(ActividadesFavoritas).\
            filter(ActividadesFavoritas.actividad_id == idActividad).first()

        return actividad

    def updateLikeActividad(self, usuarioId, idActividad, nuevoLike):
        nuevaActividad = self.getActividad(idActividad)
        nuevaActividad.like = nuevoLike

        self.db_session.add(nuevaActividad)
        self.db_session.commit()


    def actividadesFavoritasUsuario(self, usuarioID):
        actividades = self.db_session.query(
            Actividad.nombre,
            Actividad.valoracion,
            Actividad.duracion,
            Usuario.nombre,
            ActividadesFavoritas.like,
            ).\
        join(Actividad, ActividadesFavoritas.actividad_id == Actividad.id).\
        join(Usuario, ActividadesFavoritas.usuario_id == Usuario.id).\
        filter(Usuario.id == usuarioID).\
        filter(ActividadesFavoritas.like == 1).all()

        return actividades
    

    """ def actividadesFavoritasUsuario(self, usuarioID):
        lugaresFavoritosUsuario = self.db_session.query(
            Actividad.nombre,
            Ciudad.nombre,
            Usuario.nombre,
            LugaresFavoritos.like,
            ).\
        join(Lugar, LugaresFavoritos.lugar_id == Lugar.id).\
        join(Usuario, LugaresFavoritos.usuario_id == Usuario.id).\
        join(Ciudad,Lugar.id_ciudad == Ciudad.id).\
        filter(Usuario.id == usuarioID).\
        filter(LugaresFavoritos.like == 1).all()

        return lugaresFavoritosUsuario """
    

"""         self.db_session.execute(\
            update(LugaresFavoritos).\
            where(LugaresFavoritos.usuario_id == usuarioId and LugaresFavoritos.lugar_id == idLugar).\
            values(like = nuevoLike)\
        ) """


        
"""             session.exec"""  """(UserModel).\
filter
LugaresFavoritos.usuario_id == idUsuario and LugaresFavoritos.lugar_id == idLugar).\
update({LugaresFavoritos.username: 'john_deo'}) """""" session.execute(update(LugaresFavoritos).
where(LugaresFavoritos.usuario_id == idUsuario and LugaresFavoritos.lugar_id == idLugar).
values(like = False)) """