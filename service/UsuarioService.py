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

        return usuarioIniciado
    
    def agregarUsuario(self,nombre,email,contrasenia):
        with Session(getEngine()) as session:   
            nuevoUsuario = Usuario()
            nuevoUsuario.nombre = nombre
            nuevoUsuario.gmail= email
            nuevoUsuario.contrasenia = contrasenia

            session.add(nuevoUsuario)
            session.commit()

            return nuevoUsuario.id
        

    
    def agregarTokenUsuario(self, usuario, token):
        with Session(getEngine()) as session: 
            usuarioRepository = UsuarioRepository(session)
            user = usuarioRepository.getUsuarioID(usuario.id)
            
            user.token = token

            session.add(user)

            session.commit()
            print('usuario token ', user.nombre, user.token,user.contrasenia)

            return user

    def getUsuarioID(self, ID):
        with Session(getEngine()) as session:
            usuarioRepository = UsuarioRepository(session)

            usuarioObtenido = usuarioRepository.getUsuarioID(ID)

            print('service ', usuarioObtenido.nombre)
        return usuarioObtenido
    

    def getUsuarioNombre(self, nombre):
        with Session(getEngine()) as session:
            usuarioRepository = UsuarioRepository(session)

            usuario = usuarioRepository.getUsuarioNombre(nombre)

        return usuario
    
    
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
