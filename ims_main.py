import os
import socket
from pathlib import Path

from flask import Flask
from jinja2 import Environment, FileSystemLoader

import ims_api
from ims_api import products_page

app = Flask(__name__)
app.register_blueprint(products_page)


@app.route("/")
def index():
    environment = Environment(loader=FileSystemLoader("templates/"))
    template = environment.get_template("front.html")

    products_json = ims_api.all_products()
    template_dict = {
        "computerName": socket.gethostname() + " (" + socket.gethostbyname("localhost") + ")",
        "products": products_json
    }
    return template.render(template_dict)


@app.route("/health")
def health_check():
    environment = Environment(loader=FileSystemLoader("templates/"))
    template = environment.get_template("health.html")

    in_both, only_in_search, only_in_mongo = ims_api.health_check()

    sample_products = Path("static/sample_products.json").read_text()

    products_json = ims_api.all_products({})
    health_dict = {
        "computerName": socket.gethostname() + " (" + socket.gethostbyname("localhost") + ")",
        "goodProducts": [{"product_id": x} for x in in_both],
        "missingMongo": [{"product_id": x} for x in only_in_search],
        "missingES": [{"product_id": x} for x in only_in_mongo],
        "sampleProducts": sample_products,
        "products": products_json
    }

    return template.render(health_dict)


@app.route("/stats")
def analytics():
    environment = Environment(loader=FileSystemLoader("templates/"))
    template = environment.get_template("stats.html")

    in_both, only_in_search, only_in_mongo = ims_api.health_check()

    sample_products = Path("static/sample_products.json").read_text()

    health_dict = {
        "computerName": socket.gethostname() + " (" + socket.gethostbyname("localhost") + ")",
        "goodProducts": [{"product_id": x} for x in in_both],
        "missingMongo": [{"product_id": x} for x in only_in_search],
        "missingES": [{"product_id": x} for x in only_in_mongo],
        "sampleProducts": sample_products
    }

    return template.render(health_dict)


if __name__ == "__main__":
    if "IMS_SERVICE_SERVICE_PORT" in os.environ:
        app.run(host="0.0.0.0", port=int(os.environ["IMS_SERVICE_SERVICE_PORT"]))
    else:
        app.run(host="0.0.0.0", port=5000)
