from ..bd.conexion import getEngine
from sqlalchemy.orm import Session

from ..models.UsuarioCategoria import UsuarioCategoria
from ..repository.LugarRepository import LugarRepository
from ..models.LugaresFavoritos import LugaresFavoritos
from ..repository.UsuarioRepository import UsuarioRepository
from ..repository.FavoritoRepository import FavoritoRepository
from ..repository.CategoriaRepository import CategoriaRepository
from ..service.LugarService import LugarService
from ..models.Lugar import Lugar

class LugarFavoritoService:
    def __init__(self, db_session):
        self.db_session = db_session

    def getLugarFavorito(self,idUsuario,codigoLugar):
            with Session(getEngine()) as session:
                gusto = FavoritoRepository(session)

                gustoObtenido = gusto.getLugarUsuario(idUsuario,codigoLugar)

                return gustoObtenido

    def agregarGusto(self,idUsuario,lugar):
        with Session(getEngine()) as session:
            categoria = CategoriaRepository(session)
            gusto = FavoritoRepository(session)
            codigoLugar = lugar.get('codigo')
            lugarID = lugar.get('id')
            
            lugarRepository = LugarRepository(session)

            gustoObtenido = gusto.getLugarUsuario(idUsuario,codigoLugar)

            if gustoObtenido != None:   #existe en lugares favoritos
                idLugar = gustoObtenido[0]
                
                gusto.updateLike(idUsuario, idLugar, 1)
            else: #no existe en lugares
                lugarObtenido = lugarRepository.getLugar(codigoLugar)

                if lugarObtenido != None: #existe en lugar
                    print("lugar existe ", lugarObtenido)
                    nuevoMeGusta = LugaresFavoritos()
                    nuevoMeGusta.usuario_id = idUsuario
                    nuevoMeGusta.lugar_id = lugarObtenido.id
                    nuevoMeGusta.like = 1

                    session.add(nuevoMeGusta)
                    session.commit()
                    
                else: #no existe en lugar
                    lugarService = LugarService(session)

                    lugarService.guardarLugar(lugar)

                    lugarRecibido = lugarRepository.getLugar(lugar.get('id'))   
                    print("lugar no existe ",lugarRecibido)                 

                    nuevo = LugaresFavoritos()
                    nuevo.usuario_id = idUsuario
                    nuevo.lugar_id = lugarRecibido.id
                    nuevo.like = 1

                    session.add(nuevo)
                    session.commit()
            
            if gustoObtenido != None and gustoObtenido.like == 1:
                print("llego al -1")
                gusto.updateLike(idUsuario, idLugar, -1)

            categorias = categoria.getCategoriaLugar(lugarID)

            for cate in categorias:
                nuevaCategoria = UsuarioCategoria()
                nuevaCategoria.id_categorias = cate
                nuevaCategoria.id_usuario = idUsuario

                session.add(nuevaCategoria)
                session.commit()

            
    
    def quitarGusto(self,idUsuario,lugar):
        with Session(getEngine()) as session:
            gusto = FavoritoRepository(session)
            codigoLugar = lugar.get('id')
        
            gustoObtenido = gusto.getLugarUsuario(idUsuario,codigoLugar)
            
            lugarRepository = LugarRepository(session)

            if gustoObtenido != None:   
                idLugar = gustoObtenido[0]
                
                gusto.updateLike(idUsuario, idLugar, 0)
            else:
                lugarObtenido = lugarRepository.getLugar(codigoLugar)

                if lugarObtenido != None:
                    nuevoMeGusta = LugaresFavoritos()
                    nuevoMeGusta.usuario_id = idUsuario
                    nuevoMeGusta.lugar_id = lugarObtenido.id
                    nuevoMeGusta.like = 0

                    session.add(nuevoMeGusta)
                    session.commit()
                    
                else:
                    lugarService = LugarService(session)

                    lugarService.guardarLugar(lugar)

                    lugarRecibido = lugarRepository.getLugar(lugar.get('id'))   
                    print("lugar",lugarRecibido)                 

                    nuevo = LugaresFavoritos()
                    nuevo.usuario_id = idUsuario
                    nuevo.lugar_id = lugarRecibido.id
                    nuevo.like = 0

                    session.add(nuevo)
                    session.commit()
        
            if gustoObtenido != None and gustoObtenido.like == 0:
                gusto.updateLike(idUsuario, idLugar, -1)

    def gustosUsuario(self,idUsuario):
        with Session(getEngine()) as session:
            gustoRepository = FavoritoRepository(session)

            gustos = gustoRepository.favoritosUsuario(idUsuario)
        
            return gustos