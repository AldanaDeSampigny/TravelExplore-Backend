import datetime
import re
from turtle import update
import json

from ..models.CiudadCategoria import CiudadCategoria
from ..models.Categoria import Categoria
from ..models.LugarCategoria import LugarCategoria

from ..repository.CategoriaRepository import CategoriaRepository

from ..models.Ciudad import Ciudad
from ..models.Horario import Horario
from ..models.Lugar import Lugar
from ..repository.LugarRepository import LugarRepository

from ..bd.conexion import getEngine
from sqlalchemy.orm import Session

class LugarService:
    def __init__(self, db_session):
        self.db_session = db_session

    def guardarLugar(self, lugar):
        with Session(getEngine()) as session:
            repository = LugarRepository(session)

            if lugar['tipo'] == 'city' or lugar['tipo'] == 'locality':
                self.guardarCiudad(lugar)
                return

            lugarEncontrado = repository.getLugar(lugar['id'])
            if lugarEncontrado:
                lugarCate = repository.getLugarCategoria(lugarEncontrado.id)
                if not lugarCate:
                    self.guardarCategoria(lugarEncontrado, lugar['tipo'])
            
                if(lugarEncontrado.valoracion is None or lugarEncontrado.imagen is None):
                    lugarEncontrado.valoracion = lugar['valoracion'] if lugar['valoracion'] != 'N/A' else 0
                    lugarEncontrado.imagen = lugar['imagen']

                session.add(lugarEncontrado)
                session.commit()
            else: 
                nuevoLugar = Lugar()
                nuevoLugar.codigo = lugar['id']
                nuevoLugar.nombre = lugar['nombre']
                nuevoLugar.tipo = lugar['tipo']
                nuevoLugar.latitud = lugar['latitud']
                nuevoLugar.longitud = lugar['longitud']
                nuevoLugar.valoracion = lugar['valoracion'] if lugar['valoracion'] != 'N/A' else 0
                nuevoLugar.imagen = lugar['imagen']

                ciudad = repository.getCiudadLugar(lugar['ciudad'])
                if ciudad:
                    nuevoLugar.id_ciudad = ciudad.id
                    print("ciudad existe, guardado")
                else:
                    nuevoCiudad = Ciudad()
                    nuevoCiudad.nombre = lugar['ciudad']
                    session.add(nuevoCiudad)
                    session.commit()
                    nuevoLugar.id_ciudad = nuevoCiudad.id
                    print("ciudad no existe, a guardao")

                session.add(nuevoLugar)
                session.commit()

                self.guardarCategoria(nuevoLugar, lugar['tipo'])

                horarios = lugar.get('horarios', [])
                for dia in horarios:
                    horarioDia = dia.split(': ')
                    day = horarioDia[0].strip()
                    for horario_part in horarioDia:
                        if ':' in horario_part:
                            for part in horario_part.split(','):
                                rangoTiempo = part.replace('\u202f', ' ').replace('\u2009', ' ')
                                if ':00 –' in rangoTiempo:
                                    rangoTiempo = rangoTiempo.replace(
                                        ':00 –', ':00\u202fPM –')
                                elif ':30 –' in rangoTiempo:
                                    rangoTiempo = rangoTiempo.replace(
                                        ':30 –', ':30\u202fPM –')
                                
                                horas = re.findall(r'\d+:\d+\s*[APapMm]+', rangoTiempo)
                                if len(horas) == 2:
                                    hora_inicio_str, hora_fin_str = horas
                                    hora_inicio = datetime.datetime.strptime(
                                        hora_inicio_str, '%I:%M %p').strftime('%H:%M:%S')
                                    hora_fin = datetime.datetime.strptime(
                                        hora_fin_str, '%I:%M %p').strftime('%H:%M:%S')
                                    
                                    horario = Horario()
                                    horario.id_lugar = nuevoLugar.id
                                    horario.dia = day
                                    horario.horaInicio = hora_inicio
                                    horario.horaFin = hora_fin

                                    session.add(horario)
                                    session.commit()
                                else:
                                    print("No se encontró un formato de hora válido en:", rangoTiempo)
                        
            print("se guardo")

    def guardarCategoria(self, lugar, categoriaNombre):
        with Session(getEngine()) as session:
            repository = CategoriaRepository(session)
            categoria = repository.getCategoriaNombre(categoriaNombre)

            if categoria:
                nuevoLugarCategoria = LugarCategoria()
                nuevoLugarCategoria.id_lugar = lugar.id
                nuevoLugarCategoria.id_categoria = categoria.id

                session.add(nuevoLugarCategoria)
                session.commit()
            else:
                nuevaCategoria = Categoria()
                nuevaCategoria.nombre = categoriaNombre

                session.add(nuevaCategoria)
                session.commit()

                nuevoLugarCategoria = LugarCategoria()
                nuevoLugarCategoria.id_lugar = lugar.id
                nuevoLugarCategoria.id_categoria = nuevaCategoria.id

                session.add(nuevoLugarCategoria)
                session.commit()

    def guardarCategoriaCiudad(self, ciudad, categoriaNombre):
        with Session(getEngine()) as session:
            repository = CategoriaRepository(session)
            categoria = repository.getCategoriaNombre(categoriaNombre)

            if categoria:
                nuevoCiudadCategoria = CiudadCategoria()
                nuevoCiudadCategoria.id_ciudad = ciudad.id
                nuevoCiudadCategoria.id_categoria = categoria.id

                session.add(nuevoCiudadCategoria)
                session.commit()
                print("nosexd ", nuevoCiudadCategoria)
            else:
                nuevaCategoria = Categoria()
                nuevaCategoria.nombre = categoriaNombre

                session.add(nuevaCategoria)
                session.commit()

                nuevoCiudadCategoria = CiudadCategoria()
                nuevoCiudadCategoria.id_ciudad = ciudad.id
                nuevoCiudadCategoria.id_categoria = nuevaCategoria.id

                session.add(nuevoCiudadCategoria)
                session.commit()

    def guardarCiudad(self, ciudad):
        with Session(getEngine()) as session:
            repository = LugarRepository(session)

            ciudadExistente = repository.getCiudad(ciudad['id'])
            if not ciudadExistente:
                nuevaCiudad = Ciudad()
                nuevaCiudad.codigo = ciudad['id']
                nuevaCiudad.nombre = ciudad['nombre']
                nuevaCiudad.latitud = ciudad['latitud']
                nuevaCiudad.longitud = ciudad['latitud']

                session.add(nuevaCiudad)
                session.commit()

                self.guardarCategoriaCiudad(nuevaCiudad, ciudad['tipo'])
                print("se guardo")
                
            elif ciudadExistente:
                ciudadCate = repository.getCiudadCategoria(ciudadExistente.id)
                if not ciudadCate:
                    self.guardarCategoriaCiudad(ciudadExistente, ciudad['tipo'])
            
                if ciudadExistente.codigo is None or ciudadExistente.latitud is None or ciudadExistente.longitud is None:
                    ciudadExistente.codigo = ciudad['id']
                    ciudadExistente.latitud = ciudad['latitud']
                    ciudadExistente.longitud = ciudad['latitud']
                                        
                    session.add(ciudadExistente)
                    session.commit()
                    print("se modifico ciudad")

    def getLugarByID(self,id):
        with Session(getEngine()) as session:
            repository = LugarRepository(session)
            lugarEncontrado = repository.getLugarID(id)
            
        return lugarEncontrado
#primero basico, luego que guarde los horarios en una nueva tabla, y luego dividir si son ciudades pa q las guarde
    def guardarSitio(self, sitio): 
        tipoSitio = sitio.get('tipo', 'N/A')
        print(tipoSitio)

        switch_dict = {
            'point_of_interest': self.guardarLugar,
            'establishment': self.guardarLugar,
            'park': self.guardarLugar,
            'restaurant': self.guardarLugar,
            'place_of_worship': self.guardarLugar,
            'tourist_attraction': self.guardarLugar,
            'store': self.guardarLugar,
            'food': self.guardarLugar,
            'museum': self.guardarLugar,
            'electronics_store': self.guardarLugar,
            'church': self.guardarLugar,
            'tourist_attraction': self.guardarLugar,
            'insurance_agency': self.guardarLugar,
            'lodging': self.guardarLugar,
            'bar': self.guardarLugar,
            'night_club': self.guardarLugar,
            'spa': self.guardarLugar,
            'beauty_salon': self.guardarLugar,
            'travel_agency': self.guardarLugar,
            'cafe': self.guardarLugar,
            'city': self.guardarCiudad,
            'country': self.guardarCiudad,
            'locality': self.guardarCiudad,
        }

        if tipoSitio in switch_dict:
            switch_dict[tipoSitio](sitio)

    def guardarValoracionUsuario(self, id, valoracion):
        with Session(getEngine()) as session:
            lugarRepository = LugarRepository(session)
            lugarConValoracion = lugarRepository.agregarValoracionUsuario(id, valoracion)
        return lugarConValoracion

    def guardarResenia(self,lugarID,resenia,idUsuario):
        with Session(getEngine()) as session:
            lugarRepository = LugarRepository(session)
            reseniaAgregada = lugarRepository.agregarReseña(lugarID,resenia,idUsuario)
        return reseniaAgregada
    
    def getUltimasResenias(self,lugarID):
        with Session(getEngine()) as session:
            lugarRepo = LugarRepository(session)
            
            resenias = lugarRepo.ultimasReseñas(lugarID)
        return resenias
    
    def obtenerValoracionUsuario(self,codigoLugar):
        with Session(getEngine()) as session:
            lugarRepo = LugarRepository(session)

            valoracionUsuario = lugarRepo.getValoracionUsuario(codigoLugar)
        return valoracionUsuario
