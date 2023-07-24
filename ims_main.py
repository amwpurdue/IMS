from flask import Flask, jsonify
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import socket

import ims_api
from ims_api import products_page

app = Flask(__name__)
app.register_blueprint(products_page)


@app.route("/")
def index():
    environment = Environment(loader=FileSystemLoader("templates/"))
    template = environment.get_template("front.html")

    products_json = ims_api.get_products().json
    template_dict = {
        "computerName": socket.gethostname() + " (" + socket.gethostbyname("localhost") + ")",
        "products": products_json["products"]
    }
    return template.render(template_dict)


@app.route("/health")
def health_check():
    environment = Environment(loader=FileSystemLoader("templates/"))
    template = environment.get_template("health.html")

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
    app.run(host="0.0.0.0", port=5000)
