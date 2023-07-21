from flask import Blueprint, request, jsonify
from pymongo import MongoClient
import os
import uuid

PRODUCTS_COL = "products"

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


@productsPage.route("/", methods=["GET"])
def getProducts():
    db = get_database()

    productList = []
    for p in db[PRODUCTS_COL].find():
        productList.append({
            "product_id": p.get("product_id"),
            "name": p.get("name"),
            "category": p.get("category"),
            "price": p.get("price"),
            "quantity": p.get("quantity")
        })
    return jsonify({"products": productList})


@productsPage.route("/", methods=["POST"])
def addProduct():
    content_type = request.headers.get('Content-Type')
    print(content_type)
    if content_type == 'application/json':
        print("got json")

    db = get_database()

    product_id = str(uuid.uuid4())
    db[PRODUCTS_COL].insert_one({
        "product_id": product_id,
        "name": request.form.get("name"),
        "category": request.form.get("category"),
        "price": request.form.get("price"),
        "quantity": request.form.get("quantity")
    })
    return "Successfully added new product"
