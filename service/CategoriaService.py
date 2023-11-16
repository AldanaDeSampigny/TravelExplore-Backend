from ..models.UsuarioCategoria import UsuarioCategoria
from ..repository.CategoriaRepository import CategoriaRepository
from ..bd.conexion import getEngine
from sqlalchemy.orm import Session


class CategoriaService:
    def __init__(self, db_session):
        self.db_session = db_session

    def getCategorias(self):
        with Session(getEngine()) as session:
            categoriaRepository = CategoriaRepository(session)

            categorias = categoriaRepository.getCategorias()

        return categorias
    
    def guardarGustos(self, usuarioID, idsGustos):
        with Session(getEngine()) as session:
            for i in range(0, len(idsGustos)):
                usuarioCategoriaNuevo = UsuarioCategoria()
                usuarioCategoriaNuevo.id_usuario = usuarioID
                usuarioCategoriaNuevo.id_categorias = idsGustos[i]

                session.add(usuarioCategoriaNuevo)
                session.commit()
