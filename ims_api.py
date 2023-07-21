from flask import Blueprint
from pymongo import MongoClient
import os

productsPage = Blueprint("products_page", __name__, url_prefix="/products")

def get_database():
    if ("db_root_password" in os.environ):
        client = MongoClient(
            host=os.environ["MY_RELEASE_MONGODB_SERVICE_HOST"] + ":" + os.environ["MY_RELEASE_MONGODB_SERVICE_PORT"],
            username="root",
            password=os.environ["db_root_password"]
        )
    else:
        client = MongoClient(
            host=os.environ["MY_RELEASE_MONGODB_SERVICE_HOST"] + ":" + os.environ["MY_RELEASE_MONGODB_SERVICE_PORT"]
        )

    return client[os.environ["db_name"]]


@productsPage.route("/")
def getProducts():
    return "products"
