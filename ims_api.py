from flask import Blueprint, request, jsonify
from pymongo import MongoClient
import os
import uuid

from search_handler import SearchHandler

PRODUCTS_COL = "products"

products_page = Blueprint("products_page", __name__, url_prefix="/products")

if "es_index" in os.environ:
    search_handler = SearchHandler(os.environ["es_index"])
else:
    search_handler = SearchHandler("search-ims-test")


def get_database():
    if "db_root_password" in os.environ:
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


def get_product_from_db_result(db_result):
    if db_result is None:
        return None

    pid = db_result.get("product_id")
    s_results = search_handler.get_product(pid)
    full_product = {
        "product_id": db_result.get("product_id"),
        "name": db_result.get("name"),
        "category": db_result.get("category"),
        "price": db_result.get("price"),
        "quantity": db_result.get("quantity")
    }
    if s_results is None:
        return full_product
    return full_product | s_results["_source"]


@products_page.route("/", methods=["GET"])
def get_products():
    db = get_database()

    product_list = []
    for p in db[PRODUCTS_COL].find():
        product_list.append(get_product_from_db_result(p))
    return jsonify({"products": product_list})


@products_page.route("/<product_id>/", methods=["GET"])
def get_product(product_id):
    db = get_database()

    p = db[PRODUCTS_COL].find_one({"product_id": product_id})
    return jsonify(get_product_from_db_result(p))


@products_page.route("/<product_id>/", methods=["DELETE"])
def delete_product(product_id):
    return "deleted " + product_id


@products_page.route("/search", methods=["GET"])
def search_products():
    keywords = request.args.get("keywords")
    db = get_database()

    product_list = []
    for res in search_handler.search_product(keywords):
        p = db[PRODUCTS_COL].find_one({"product_id": res})
        if p is not None:
            product_list.append(get_product_from_db_result(p))
    return product_list


@products_page.route("/", methods=["POST"])
def add_product():
    content_type = request.headers.get('Content-Type')
    print(content_type)
    if content_type == 'application/json':
        print("got json")
    if check_input("name"):
        return "Missing name"
    if check_input("category"):
        return "Missing category"
    if check_input("price"):
        return "Missing price"
    if check_input("quantity"):
        return "Missing quantity"
    if check_input("description"):
        return "Missing description"
    db = get_database()

    product_id = str(uuid.uuid4())
    db[PRODUCTS_COL].insert_one({
        "product_id": product_id,
        "name": request.form.get("name"),
        "category": request.form.get("category"),
        "price": request.form.get("price"),
        "quantity": request.form.get("quantity")
    })

    search_handler.add_product(product_id, request.form.get("name"), request.form.get("description"))
    return "Successfully added new product. <br><a href=\"/\">Home.</a>"


def check_input(key):
    return key not in request.form or len(request.form.get(key).strip()) == 0
