from ..models.Categoria import Categoria
from ..models.UsuarioCategoria import UsuarioCategoria
from ..models.Usuario import Usuario

class CategoriaRepository:

    def __init__(self, db_session): #esto seria un constructor
        self.db_session = db_session

    def getCategoriaUsuario(self, usuarioID):
        id = int(usuarioID)
        categorias = self.db_session.query(Categoria.id).\
            join(UsuarioCategoria, Categoria.id == UsuarioCategoria.id_categorias).\
            filter(UsuarioCategoria.id_usuario == id)

        result = categorias.all()
        return result


    """ def getUsuarioCategoria(self, usuarioID):
        categorias = self.db_session.query(Categoria.id).\
            join(UsuarioCategoria, Categoria.id == UsuarioCategoria.id_categorias).\
            filter(UsuarioCategoria.id_usuarios == usuarioID).all()
            return categorias """

    def getCategorias(self):
        categorias = self.db_session.query().all

        return categorias