from ..models.Usuario import Usuario
from ..models.Categoria import Categoria
from ..models.UsuarioCategoria import UsuarioCategoria
from sqlalchemy.orm import sessionmaker

class UsuarioRepository:
    def __init__(self, db_session): #esto seria un constructor
        self.db_session = db_session

    def getUsuarios(self):
        usuarios = self.db_session.query(Usuario)
        
        return usuarios.all()

    # def getUsuarioCategoria(self, usuarioID):
    #     categorias = self.db_session.query(Categoria.id).\
    #         join (Categoria, Categoria.id == UsuarioCategoria.id_categorias).\
    #         join (Usuario, Usuario.id == UsuarioCategoria.id_usuarios).\
    #         filter(Usuario.id == usuarioID).all()

    #     return categorias