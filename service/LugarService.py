import datetime
import re
from turtle import update
import json

from ..models.Pais import Pais
from ..models.Provincia import Provincia
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

            lugar_existente = repository.getLugar(lugar['id'])
            if not lugar_existente:
                nuevoLugar = Lugar()
                nuevoLugar.codigo = lugar['id']
                nuevoLugar.nombre = lugar['nombre']
                nuevoLugar.tipo = lugar['tipo']
                nuevoLugar.latitud = lugar['latitud']
                nuevoLugar.longitud = lugar['longitud']

                ciudad = repository.getCiudadLugar(lugar['ciudad'])
                if ciudad:
                    nuevoLugar.id_ciudad = ciudad.id
                    print("ciudad existe, guardao")
                else:
                    nuevoCiudad = Ciudad()
                    nuevoCiudad.nombre = lugar['ciudad']
                    session.add(nuevoCiudad)
                    session.commit()
                    nuevoLugar.id_ciudad = nuevoCiudad.id
                    print("ciudad no existe, a guardao")

                session.add(nuevoLugar)
                session.commit()

                horarios = lugar.get('horarios', [])
                for dia in horarios:
                    # Dividir la cadena de horario en días y rangos de tiempo
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
            else:
                print("ya existe")

    def guardarCiudad(self, ciudad):
        with Session(getEngine()) as session:
            repository = LugarRepository(session)

            ciudadExistente = repository.getCiudad(ciudad['id'], ciudad['nombre'])
            if not ciudadExistente:
                nuevaCiudad = Ciudad()
                nuevaCiudad.codigo = ciudad['id']
                nuevaCiudad.nombre = ciudad['nombre']

                provincia = repository.getProvinciaCiudad(ciudad['provincia'])
                if provincia:
                    nuevaCiudad.id_provincia = provincia.id
                else:
                    nuevoProvincia = Provincia()
                    nuevoProvincia.nombre = ciudad['provincia']
                    session.add(nuevoProvincia)
                    session.commit()
                    nuevaCiudad.id_provincia = nuevoProvincia.id
                    print("forma pa guardar provincia")

                session.add(nuevaCiudad)
                session.commit()
                print("se guardo")
            elif ciudadExistente.codigo is None or ciudadExistente.id_pais is None:
                ciudadExistente.codigo = ciudad['id']
                provincia = repository.getProvinciaCiudad(ciudad['pais'])
                if provincia:
                    ciudadExistente.id_provincia = provincia.id
                else:
                    nuevoProvincia = Provincia()
                    nuevoProvincia.nombre = provincia['pais']
                    session.add(nuevoProvincia)
                    session.commit()
                    ciudadExistente.id_pais = nuevoProvincia.id

                session.add(ciudadExistente)
                session.commit()
                print("se modifico ciudad")

    def guardarProvincia(self, provincia):
        with Session(getEngine()) as session:
            repository = LugarRepository(session)

            provinciaExistente = repository.getProvincia(provincia['id'], provincia['nombre'])
            if not provinciaExistente:
                nuevaProvincia = Provincia()
                nuevaProvincia.codigo = provincia['id']
                nuevaProvincia.nombre = provincia['nombre']

                pais = repository.getPaisProvincia(provincia['pais'])
                if pais:
                    nuevaProvincia.id_pais = pais.id
                else:
                    nuevoPais = Pais()
                    nuevoPais.nombre = provincia['pais']
                    session.add(nuevoPais)
                    session.commit()
                    nuevaProvincia.id_pais = nuevoPais.id
                    print("forma para guardar pais")

                session.add(nuevaProvincia)
                session.commit()
                print("se guardo")
            elif provinciaExistente.codigo is None or provinciaExistente.id_pais is None:
                provinciaExistente.codigo = provincia['id']
                pais = repository.getPaisProvincia(provincia['pais'])
                if pais:
                    provinciaExistente.id_pais = pais.id
                else:
                    nuevoPais = Pais()
                    nuevoPais.nombre = provincia['pais']
                    session.add(nuevoPais)
                    session.commit()
                    provinciaExistente.id_pais = nuevoPais.id

                session.add(provinciaExistente)
                session.commit()
                print("se modifico provincia")

    def guardarPais(self, pais):
        with Session(getEngine()) as session:
            repository = LugarRepository(session)

            paisExistente = repository.getPais(pais['id'], pais['nombre'])
            if not paisExistente:
                nuevaPais = Pais()
                nuevaPais.codigo = pais['id']
                nuevaPais.nombre = pais['nombre']

                session.add(nuevaPais)
                session.commit()
                print("se guardo pais")
            elif paisExistente.codigo is None:
                paisExistente.codigo = pais['id']
                session.add(paisExistente)
                session.commit()
                print("modifico el codigo")

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
            'electronics_store': self.guardarLugar,
            #'university': self.guardarLugar,
            'city': self.guardarCiudad,
            'locality': self.guardarCiudad,
            'administrative_area_level_1': self.guardarProvincia,
            'country': self.guardarPais
        }

        if tipoSitio in switch_dict:
            switch_dict[tipoSitio](sitio)