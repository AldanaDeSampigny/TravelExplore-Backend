from ..models.ActividadesFavoritas import ActividadesFavoritas
from ..models.UsuarioCategoria import UsuarioCategoria
from ..repository.ActividadRepository import ActividadRepository
from ..repository.CategoriaRepository import CategoriaRepository
from ..bd.conexion import getEngine
from sqlalchemy.orm import Session
from ..repository.FavoritoRepository import FavoritoRepository

class ActividadFavoritaService:
    def __init__(self, db_session):
        self.db_session = db_session

    def getActividadFavorita(self,idUsuario,idActividad):
        with Session(getEngine()) as session:
            gusto = FavoritoRepository(session)

            gustoObtenido = gusto.getActividadUsuario(idUsuario,idActividad)

        return gustoObtenido

    def agregarGustoActividad(self,idUsuario,actividad):
        with Session(getEngine()) as session:
            favoritoRepository = FavoritoRepository(session)
            categoriaRepository = CategoriaRepository(session)

            idActividad = actividad.get('id')
            
            actividadRepository = ActividadRepository(session)

            gustoObtenido = favoritoRepository.getActividadUsuario(idUsuario,idActividad)

            if gustoObtenido != None:   #existe en lugares favoritos
                id = gustoObtenido[0]
                
                if gustoObtenido.like == 1:
                    print("llego al -1")
                    favoritoRepository.updateLikeActividad(idUsuario, id, -1)
                else:
                    favoritoRepository.updateLikeActividad(idUsuario, id, 1)
            else: #no existe en lugares
                actividadObtenida = actividadRepository.getActividad(idActividad)

                if actividadObtenida != None: #existe en lugar
                    print("actividad existe ", actividadObtenida)
                    nuevoMeGusta = ActividadesFavoritas()
                    nuevoMeGusta.usuario_id = idUsuario
                    nuevoMeGusta.actividad_id = actividadObtenida.id
                    nuevoMeGusta.like = 1

                    session.add(nuevoMeGusta)
                    session.commit()

            categorias = categoriaRepository.getCategoriaActividad(idActividad)

            for categoria in categorias:
                existe = categoriaRepository.getUsuarioYCategoria(idUsuario, categoria)
                print("relacion: ", existe) 
                if existe == None :
                    nuevaCategoria = UsuarioCategoria()
                    nuevaCategoria.id_categorias = categoria
                    nuevaCategoria.id_usuario = idUsuario

                    session.add(nuevaCategoria)
                    session.commit()
                else: 
                    print("existe la relacion entre: ",idUsuario, ", ", categoria)
    

    def quitarGustoActividad(self,idUsuario,actividad):
        with Session(getEngine()) as session:
            gusto = FavoritoRepository(session)

            idActividad = actividad.get('id')
            print("actividad -->" ,idActividad)
            actividadRepository = ActividadRepository(session)

            gustoObtenido = gusto.getActividadUsuario(idUsuario,idActividad)
            print("gusto obtenido actividad -->", gustoObtenido)
            if gustoObtenido != None:   #existe en lugares favoritos
                id = gustoObtenido[0]
                print("actividad NO existe ", gustoObtenido)

                
                gusto.updateLikeActividad(idUsuario, id, 0)
            else: #no existe en lugares
                actividadObtenida = actividadRepository.getActividad(idActividad)

                if actividadObtenida != None: #existe en lugar
                    print("actividad existe ", actividadObtenida)
                    print("actividad id" , actividadObtenida.id)
                    nuevoMeGusta = ActividadesFavoritas()
                    nuevoMeGusta.usuario_id = idUsuario
                    nuevoMeGusta.actividad_id = actividadObtenida.id
                    nuevoMeGusta.like = 0

                    session.add(nuevoMeGusta)
                    session.commit()
                    
                """ else: """ #no existe en lugar
                """   lugarService = LugarService(session)

                    lugarService.guardarLugar(lugar)

                    lugarRecibido = lugarRepository.getLugar(lugar.get('id'))   
                    print("lugar no existe ",lugarRecibido)                 

                    nuevo = LugaresFavoritos()
                    nuevo.usuario_id = idUsuario
                    nuevo.lugar_id = lugarRecibido.id
                    nuevo.like = 1

                    session.add(nuevo)
                    session.commit() """
            
            if gustoObtenido != None and gustoObtenido.like == 0:
                print("llego al -1")
                gusto.updateLikeActividad(idUsuario, id, -1)


    def getActividadesFavoritas(self,usuarioID):
        with Session(getEngine()) as session:
            gustoRepository = FavoritoRepository(session)

            gustos = gustoRepository.actividadesFavoritasUsuario(usuarioID)

            return gustos


    """  def gustosUsuario(self,idUsuario):
        with Session(getEngine()) as session:
            gustoRepository = FavoritoRepository(session)

            gustos = gustoRepository.favoritosUsuario(idUsuario)
        
            return gustos """