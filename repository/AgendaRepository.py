#from requests import Session
from ..models.Actividad import Actividad
from ..models.ActividadCategoria import ActividadCategoria
from ..models.Categoria import Categoria
from ..models.UsuarioCategoria import UsuarioCategoria
from ..models.Lugar import Lugar
from ..models.Ciudad import Ciudad

from sqlalchemy.orm import Session

from sqlalchemy.orm import sessionmaker
from ..models.Usuario import Usuario
from sqlalchemy import func

class AgendaRepository:
    def __init__(self, db_session): #esto seria un constructor
        self.db_session = db_session

    def crear_agenda(self, horaInicio, horaFin): 
        agenda = agenda(hora_inicio= horaInicio, hora_fin= horaFin)
        self.db_session.add(agenda)
        self.db_session.commit()
        return agenda

    """def buscarGustosPersonalizado(self, usuarioID, destinosID):
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
        return gustos        """
    

    def buscarActividad(self, usuarioID, ciudadID):
        subquery_cat_ids = self.db_session.query(Categoria.id).\
            join(UsuarioCategoria, Categoria.id == UsuarioCategoria.id_categorias).\
            filter(UsuarioCategoria.id_usuario == usuarioID).\
            subquery()

        query = self.db_session.query(Actividad.id).\
            join(ActividadCategoria, Actividad.id == ActividadCategoria.id_actividad).\
            join(Categoria, ActividadCategoria.id_categoria == Categoria.id).\
            join(UsuarioCategoria, Categoria.id == UsuarioCategoria.id_categorias).\
            join(Usuario, UsuarioCategoria.id_usuario == Usuario.id).\
            join(Lugar, Actividad.id_lugar == Lugar.id).\
            join(Ciudad, Lugar.id_ciudad == Ciudad.id).\
            filter(Usuario.id == usuarioID).\
            filter(Ciudad.id == ciudadID).\
            filter(Categoria.id.in_(subquery_cat_ids))

        result = query.all()  # Ejecutar la consulta

        return result
    
    def buscarLugar(self, actividadID):
        lugar = self.db_session.query(Lugar).\
            join(Actividad, Actividad.id_lugar == Lugar.id).\
            filter(Actividad.id == actividadID).first()
        
        return lugar
