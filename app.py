from flask import Flask, render_template

from .models.meGusta import meGustas

from .service.AgendaService import AgendaService
from .service.gustaService import gustaService

from .models.usuario import usuarios
from .models.destino import destinos
from .models.viaje import viajes
from .models.agenda import Agenda
from .bd.conexion import getSession, getEngine, Base

app = Flask(__name__)
DeDatos = getSession()
engine = getEngine()
Base.metadata.create_all(engine)

nuevo_usuario = usuarios()
nuevo_destino = destinos()
nuevo_viaje = viajes()
nueva_agenda = Agenda()
nuevo_meGusta = meGustas()

@app.route('/', methods=['GET'])
def clean_publications():
    return "Hola mundo!"

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/gustos', methods=['GET'])
def show_activity():
    gustos = gustaService().get_activities()  # Llama al método get_activities para obtener los datos
    #print (gustos)
    return render_template('gustos_detail.html', activities=gustos)

@app.route('/generar_agenda/<int:usuarioID>/<int:viajeID>', methods=['GET'])
def generar_y_mostrar_agenda(usuarioID, viajeID):
    # Llama a tu función generar_agenda con los parámetros usuarioID y viajeID
    print(usuarioID, viajeID)
    agenda_service = AgendaService(getEngine())
    agenda = agenda_service.generar_agenda(usuarioID, viajeID)
    
    # Renderiza la plantilla HTML y pasa la agenda como contexto
    return render_template('agenda.html', agenda=agenda)