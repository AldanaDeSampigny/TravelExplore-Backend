from ..repository.UsuarioRepository import UsuarioRepository
from ..bd.conexion import getEngine
from sqlalchemy.orm import Session

class UsuarioService:
    def __init__(self, db_session):
        self.db_session = db_session

    def getUsuarioIniciado(self, usuario, contraseña):
        with Session(getEngine()) as session:   
            usuarioRepository = UsuarioRepository(session)

            usuarioIniciado = usuarioRepository.getUsuarioLogin(usuario, contraseña)

            print('service ',usuarioIniciado.id)
        return usuarioIniciado.id