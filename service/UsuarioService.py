from ..models.Usuario import Usuario
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
    
<<<<<<< HEAD
    def agregarUsuario(self,nombre,email,contrasenia):
        with Session(getEngine()) as session:   
            nuevoUsuario = Usuario()
            nuevoUsuario.nombre = nombre
            nuevoUsuario.gmail= email
            nuevoUsuario.contrasenia = contrasenia

            session.add(nuevoUsuario)
            session.commit()

            return nuevoUsuario.id
=======
    def getUsuarioID(self, ID):
        with Session(getEngine()) as session:
            usuarioRepository = UsuarioRepository(session)

            usuarioIniciado = usuarioRepository.getUsuarioID(ID)

            print('service ', usuarioIniciado.nombre)
        return usuarioIniciado
    
    def editarUsuario(self, usuarioEditado):
        with Session(getEngine()) as session:
            usuarioRepository = UsuarioRepository(session)
            print('id', usuarioEditado['id'])
            usuario = usuarioRepository.getUsuarioID(usuarioEditado['id'])

            if usuario:
                print(usuario.nombre)
                usuario.nombre = usuarioEditado['nombre']
                usuario.gmail = usuarioEditado['gmail']
                usuario.imagen = usuarioEditado['imagen']
                usuario.contrasenia = usuarioEditado['contraseña']

                session.add(usuario)
                session.commit()
            else:
                print('usuario no encontrado')
>>>>>>> 06547e1bcd4cadf906dbe5e3d929f946d7f83ad5
