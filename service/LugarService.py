from turtle import update
import json

from ..models.Pais import Pais
from ..models.Provincia import Provincia
from ..models.Ciudad import Ciudad
from ..models.Horario import Horario
from ..models.Lugar import Lugar

from ..bd.conexion import getEngine
from sqlalchemy.orm import Session

class LugarService:
    def __init__(self, db_session):
        self.db_session = db_session

    def guardarLugar(self, lugar):
        with Session(getEngine()) as session:
            print(lugar)

            lugar_existente = True#session.query(Lugar).filter_by(codigo=lugar['id']).first()
            if lugar_existente:
                nuevoLugar = Lugar()
                nuevoLugar.codigo = lugar['id']
                nuevoLugar.nombre = lugar['nombre']
                nuevoLugar.tipo = lugar['tipo']
                nuevoLugar.latitud = lugar['latitud']
                nuevoLugar.longitud = lugar['longitud']
                nuevoLugar.id_ciudad = 1

                session.add(nuevoLugar)

                horarios = lugar.get('horarios', [])
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
            print(ciudad)

            ciudadExistente = True#session.query(Lugar).filter_by(codigo=lugar['id']).first()
            if ciudadExistente:
                nuevaCiudad = Ciudad()
                nuevaCiudad.codigo = ciudad['id']
                nuevaCiudad.nombre = ciudad['nombre']

                session.add(nuevaCiudad)
                session.commit()
                print("se guardo")
            else:
                print("ya existe")

    def guardarProvincia(self, provincia):
        with Session(getEngine()) as session:
            print(provincia)

            provinciaExistente = True#session.query(Lugar).filter_by(codigo=lugar['id']).first()
            if provinciaExistente:
                nuevaProvincia = Provincia()
                nuevaProvincia.codigo = provincia['id']
                nuevaProvincia.nombre = provincia['nombre']

                session.add(nuevaProvincia)
                session.commit()
                print("se guardo")
            else:
                print("ya existe")

    def guardarPais(self, pais):
        with Session(getEngine()) as session:
            print(pais)

            paisExistente = True#session.query(Lugar).filter_by(codigo=lugar['id']).first()
            if paisExistente:
                nuevaPais = Pais()
                nuevaPais.codigo = pais['id']
                nuevaPais.nombre = pais['nombre']

                session.add(nuevaPais)
                session.commit()
                print("se guardo")
            else:
                print("ya existe")

#primero basico, luego que guarde los horarios en una nueva tabla, y luego dividir si son ciudades pa q las guarde
    def guardarSitio(self, sitio): 
        tipoSitio = sitio.get('tipo', 'N/A')

        switch_dict = {
            1: self.guardarLugar,
            'city': self.guardarCiudad,
            'administrative_area_level_1': self.guardarProvincia,
            'country': self.guardarPais
        }

        if tipoSitio in switch_dict:
            switch_dict[tipoSitio](sitio)