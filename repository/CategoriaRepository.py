from ..models.Categoria import Categoria
from ..models.UsuarioCategoria import UsuarioCategoria
from ..models.Usuario import Usuario

class CategoriaRepository:

    def __init__(self, db_session): #esto seria un constructor
        self.db_session = db_session

    def getCategoriaUsuario(self, usuarioID):
        categoriasUsuario = self.db_session.query(Categoria.nombre).\
            join(Usuario, Usuario.id == UsuarioCategoria.id_usuario).\
            join(Categoria, Categoria.id == UsuarioCategoria.id_categoria).\
                filter(Usuario.id == usuarioID).all()
        
        return categoriasUsuario