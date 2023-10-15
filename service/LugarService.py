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
            print(lugar)

            lugar_existente = repository.getLugar(lugar['id'])
            #True#session.query(Lugar).filter_by(codigo=lugar['id']).first()
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
                    print("ciudad no existe, a guardao")
                    #self.guardarCiudad(lugar) #posible conflicto por codigo

                session.add(nuevoLugar)

                horarios = lugar.get('horarios', []) #ARREGLARRR
                for horario_text in horarios:
                    # Dividir la cadena de horario en días y rangos de tiempo
                    horario_parts = horario_text.split(': ')
                    print(horario_text)

                    for horario_part in horario_parts:
                        if ':' in horario_part:
                            horario_parts = horario_part.split(',')
                            for part in horario_parts:
                                day, time_range = part.split('–')
                                if time_range.strip() != "Closed":
                                    # Reemplazar guiones largos (–) con dos puntos (:)
                                    time_range = time_range.replace("–", ":")
                                    times = time_range.split('-')

                                    if len(times) == 2:
                                        hora_inicio = times[0].strip()
                                        hora_fin = times[1].strip()

                                        horario = Horario()
                                        horario.id_lugar = lugar['id']

                                        # Almacenar el día y los rangos de tiempo en la base de datos
                                        horario.dia = day.strip()
                                        horario.horaInicio = hora_inicio
                                        horario.horaFin = hora_fin

                                        session.add(horario)
                
                session.commit()
                print("se guardo")
            else:
                print("ya existe")

    def guardarCiudad(self, ciudad):
        with Session(getEngine()) as session:
            repository = LugarRepository(session)
            print(ciudad)

            ciudadExistente = repository.getCiudad(ciudad['id'])
            #True#session.query(Lugar).filter_by(codigo=lugar['id']).first()
            if not ciudadExistente:
                nuevaCiudad = Ciudad()
                nuevaCiudad.codigo = ciudad['id']
                nuevaCiudad.nombre = ciudad['nombre']

                provincia = repository.getProvinciaCiudad(ciudad['provincia'])
                if provincia:
                    nuevaCiudad.id_provincia = provincia.id
                else:
                    print("forma pa guardar provincia")

                session.add(nuevaCiudad)
                session.commit()
                print("se guardo")
            else:
                print("ya existe")

    def guardarProvincia(self, provincia):
        with Session(getEngine()) as session:
            repository = LugarRepository(session)

            print(provincia)

            provinciaExistente = repository.getProvincia(provincia['id'])
            #True#session.query(Lugar).filter_by(codigo=lugar['id']).first()
            if not provinciaExistente:
                nuevaProvincia = Provincia()
                nuevaProvincia.codigo = provincia['id']
                nuevaProvincia.nombre = provincia['nombre']

                pais = repository.getPaisProvincia(provincia['pais'])
                if pais:
                    nuevaProvincia.id_pais = pais.id
                else:
                    print("forma para guardar pais")

                session.add(nuevaProvincia)
                session.commit()
                print("se guardo")
            else:
                print("ya existe")

    def guardarPais(self, pais):
        with Session(getEngine()) as session:
            repository = LugarRepository(session)

            print(pais)

            paisExistente = repository.getPais(pais['id'])
            #True#session.query(Lugar).filter_by(codigo=lugar['id']).first()
            if not paisExistente:
                nuevaPais = Pais()
                nuevaPais.codigo = pais['id']
                nuevaPais.nombre = pais['nombre']

                session.add(nuevaPais)
                session.commit()
                print("se guardo pais")
            else:
                print("ya existe")

#primero basico, luego que guarde los horarios en una nueva tabla, y luego dividir si son ciudades pa q las guarde
    def guardarSitio(self, sitio): 
        tipoSitio = sitio.get('tipo', 'N/A')
        print(tipoSitio)

        switch_dict = {
            'point_of_interest': self.guardarLugar,
            'establishment': self.guardarLugar,
            'restaurant': self.guardarLugar,
            'city': self.guardarCiudad,
            'locality': self.guardarCiudad,
            'administrative_area_level_1': self.guardarProvincia,
            'country': self.guardarPais
        }

        if tipoSitio in switch_dict:
            switch_dict[tipoSitio](sitio)