from ..models.ActividadCategoria import ActividadCategoria
from ..models.Categoria import Categoria
from ..models.UsuarioCategoria import UsuarioCategoria
from ..models.Usuario import Usuario

class CategoriaRepository:

    def __init__(self, db_session): #esto seria un constructor
        self.db_session = db_session

    def getCategoriaNombre(self, nombreCategoria):
        categoria = self.db_session.query(Categoria).\
            filter(Categoria.nombre == nombreCategoria).first()
        
        return categoria

    def getCategoriaUsuario(self, usuarioID):
        id = int(usuarioID)
        categorias = self.db_session.query(Categoria.id).\
            join(UsuarioCategoria, Categoria.id == UsuarioCategoria.id_categorias).\
            filter(UsuarioCategoria.id_usuario == id)

        result = categorias.all()
        return result
    
    def getCategoriaActividad(self, actividadID):
        catActividad = self.db_session.query(Categoria.id).\
            join(ActividadCategoria, Categoria.id == ActividadCategoria.id_categoria).\
            filter(ActividadCategoria.id_actividad == actividadID)
        
        result = [row[0] for row in catActividad.all()]  # Extrae los identificadores
    
        return result

    def getCategorias(self):
        categorias = self.db_session.query(Categoria).all()

        return categorias