from flask import jsonify

import googlemaps
from datetime import datetime, timedelta

def obtenerDirecciones(origen, destino, transporte):
    if not origen or not destino:
        return jsonify({'error': 'Se requieren las coordenadas de origen y destino'})

    gmaps_directions = googlemaps.Client(key='AIzaSyAQ2FMwWtoGGlOE5Urq3QmyX7hHG8G0wi0')

    # Realizar la solicitud a la API Directions
    directions_result = gmaps_directions.directions(origen, destino, mode=transporte)

    # Verificar si la solicitud fue exitosa
    if directions_result:
        # Obtener información sobre la ruta y el tiempo de traslado
        ruta = directions_result[0]
        distancia = ruta['legs'][0]['distance']['text']
        tiempo_traslado_str = ruta['legs'][0]['duration']['text']

        # Parsear la cadena de tiempo de traslado
        partes_tiempo = tiempo_traslado_str.split()
        horas, minutos, segundos = 0, 0, 0

        for i, parte in enumerate(partes_tiempo):
            if parte == 'h':
                horas = int(partes_tiempo[i - 1])
            elif parte == 'min':
                minutos = int(partes_tiempo[i - 1])
            elif parte == 's':
                segundos = int(partes_tiempo[i - 1])

        # Crear un objeto timedelta con los valores calculados
        tiempo_traslado = timedelta(hours=horas, minutes=minutos, seconds=segundos)
        if(transporte == "transit"):
            tiempo_traslado += timedelta(minutes=20)
        else:
            tiempo_traslado += timedelta(minutes=5)

        return tiempo_traslado