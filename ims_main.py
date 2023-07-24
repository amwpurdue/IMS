from flask import Flask
from jinja2 import Environment, FileSystemLoader
import socket

import ims_api
from ims_api import products_page

app = Flask(__name__)
app.register_blueprint(products_page)


@app.route("/")
def index():
    environment = Environment(loader=FileSystemLoader("templates/"))
    template = environment.get_template("index.html")

    template_dict = {
        "computerName": socket.gethostname() + " (" + socket.gethostbyname("localhost") + ")"
    }

    return template.render(template_dict)


@app.route("/front")
def frontend():
    environment = Environment(loader=FileSystemLoader("templates/"))
    template = environment.get_template("front.html")

    products_json = ims_api.get_products().json
    template_dict = {
        "computerName": socket.gethostname() + " (" + socket.gethostbyname("localhost") + ")",
        "products": products_json["products"]
    }
    print(template_dict)
    return template.render(template_dict)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
