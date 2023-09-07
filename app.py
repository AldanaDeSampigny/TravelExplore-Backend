from flask import Flask, render_template

from .presenter.gustaPresenter import gustaPresenter

from .models.meGusta import meGusta
from .models.usuario import usuario
from .models.destino import destino
from .models.viaje import viajes
from .models.agenda import Agenda
from .bd.conexion import getSession, getEngine, Base

app = Flask(__name__)
DeDatos = getSession()
engine = getEngine()
Base.metadata.create_all(engine)
gustoPresenter = gustaPresenter()

nuevo_usuario = usuario()
nuevo_destino = destino()
nuevo_viaje = viajes()
nueva_agenda = Agenda()
nuevo_meGusta = meGusta()


@app.route('/', methods=['GET'])
def clean_publications():
    return "Hola mundo!"

if __name__ == '__main__':
    app.run(debug=True)

#@app.route('/activity/<int:activity_id>', methods=['GET'])
@app.route('/gustos', methods=['GET'])
def show_activity():
    gustos = gustoPresenter.get_activities()  # Obtén una actividad específica por su ID desde el Presenter
    return render_template('gustos_detail.html', gustos=gustos)
