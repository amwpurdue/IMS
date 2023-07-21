from flask import Flask
from jinja2 import Environment, FileSystemLoader
import socket

import ims_api
from ims_api import productsPage

app = Flask(__name__)
app.register_blueprint(productsPage)


@app.route("/")
def index():
    environment = Environment(loader=FileSystemLoader("templates/"))
    template = environment.get_template("index.html")

    indexDict = {
        "computerName": socket.gethostname() + " (" + socket.gethostbyname("localhost") + ")"
    }

    return template.render(indexDict)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)