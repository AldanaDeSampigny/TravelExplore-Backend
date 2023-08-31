from flask import Flask

app = Flask(__name__)

##@app.route("/")
# def hello_world():
#     return "<p>Hello, World!</p>"

@app.route('/', methods=['GET'])
def clean_publications():
    return "Hola mundo!"

#schedule_automatic_trains()

