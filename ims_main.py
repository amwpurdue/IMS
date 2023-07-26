import os
import datetime
import socket
from pathlib import Path

from flask import Flask, request
from jinja2 import Environment, FileSystemLoader

import ims_api
from ims_api import products_page

app = Flask(__name__)
app.register_blueprint(products_page)


@app.route("/")
def index():
    environment = Environment(loader=FileSystemLoader("templates/"))
    template = environment.get_template("front.html")

    template_dict = {
        "computerName": socket.gethostname() + " (" + socket.gethostbyname("localhost") + ")"
    }

    if "keywords" in request.args:
        keywords = request.args["keywords"]
        products_json = ims_api.get_products_with_keywords(keywords)
        template_dict.update({"search_keywords": keywords})
    else:
        products_json = ims_api.all_products()

    template_dict.update({"products": products_json})

    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    db = ims_api.get_database()
    db["visitors"].update_one(
        {"ip": ip},
        {"$set": {"ip": ip, "last_modified": datetime.datetime.now(tz=datetime.timezone.utc)}},
        upsert=True
    )

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


if __name__ == "__main__":
    if "IMS_SERVICE_SERVICE_PORT" in os.environ:
        app.run(host="0.0.0.0", port=int(os.environ["IMS_SERVICE_SERVICE_PORT"]))
    else:
        app.run(host="0.0.0.0", port=5000)
