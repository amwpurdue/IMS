import os
import uuid

from flask import Blueprint, request, jsonify
from pymongo import MongoClient, ReturnDocument

from search_handler import SearchHandler

PRODUCTS_COL = "products"

products_page = Blueprint("products_page", __name__, url_prefix="/products")

if "es_index" in os.environ:
    search_handler = SearchHandler(os.environ["es_index"])
else:
    search_handler = SearchHandler("search-ims-test")

INPUT_MAP = [
    ("name", str),
    ("category", str),
    ("price", float),
    ("quantity", int),
    ("description", str)
]


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


def mongo_product_to_dict(db_result):
    if db_result is None:
        return None

    fields = ["product_id"] + [x[0] for x in INPUT_MAP]
    return dict([(key, db_result[key]) for key in fields])


@products_page.route("/", methods=["GET"])
def get_products():
    db = get_database()

    product_list = []
    for p in db[PRODUCTS_COL].find({"quantity": {"$gt": 0}}):
        product_list.append(mongo_product_to_dict(p))
    return jsonify({"products": product_list})


def health_check():
    all_from_search = set(search_handler.get_all())

    db = get_database()
    mongo_list = set([p.get("product_id") for p in db[PRODUCTS_COL].find()])

    in_both = all_from_search.intersection(set(mongo_list))
    only_in_search = all_from_search - in_both
    only_in_mongo = mongo_list - in_both

    return in_both, only_in_search, only_in_mongo


@products_page.route("/<product_id>/", methods=["GET"])
def get_product(product_id):
    db = get_database()

    p = db[PRODUCTS_COL].find_one({"product_id": product_id})
    return jsonify(mongo_product_to_dict(p))


@products_page.route("/<product_id>/", methods=["DELETE"])
def delete_product(product_id):
    db = get_database()

    db[PRODUCTS_COL].delete_one({"product_id": product_id})
    search_handler.delete_product(product_id)
    return jsonify({"success": product_id}), 200


@products_page.route("/<product_id>/", methods=["POST"])
def buy_product(product_id):
    db = get_database()
    update_response = db[PRODUCTS_COL].find_one_and_update(
        {"product_id": product_id},
        {"$inc": {"quantity": -1}},
        return_document=ReturnDocument.AFTER
    )
    if update_response is not None:
        return jsonify({"success": product_id, "product": mongo_product_to_dict(update_response)}), 200

    return jsonify({"error": update_response}), 500


@products_page.route("/", methods=["DELETE"])
def delete_products():
    """
    json should be of the form
    single product {"product_id": "uuid"}
    or
    {"products":[array of products]"}
    """

    if request.headers.get('Content-Type') != 'application/json':
        return jsonify({"error": "json content-type required"}), 400

    input_json = request.json
    if "products" in input_json:
        result = list()
        for json_element in input_json["products"]:
            response_single = delete_product(json_element["product_id"])
            if response_single[1] != 200:
                return response_single
            result.append(response_single[0].json)
        return jsonify({"success": result}), 200

    result = delete_product(input_json["product_id"])
    return jsonify({"success": result}), 200


@products_page.route("/search", methods=["GET"])
def search_products():
    keywords = request.args.get("keywords")
    db = get_database()

    product_list = []
    for res in search_handler.search_product(keywords):
        p = db[PRODUCTS_COL].find_one({"product_id": res})
        if p is not None:
            product_list.append(mongo_product_to_dict(p))
    return product_list


@products_page.route("/", methods=["POST"])
def add_products():
    """
    json should be of the form
    single product {"name": string, etc}

    or

    {"products":[array of products]"}
    """
    if request.headers.get('Content-Type') != 'application/json':
        return jsonify({"error": "json content-type required"}), 400

    input_json = request.json
    if "products" in input_json:
        result = list()
        for json_element in input_json["products"]:
            response_single = add_product(json_element)
            if response_single[1] != 200:
                return response_single
            result.append(response_single[0].json)
        return jsonify({"success": result}), 200

    return add_product(input_json)


def add_product(input_json):
    product_dict = dict()
    try:
        for key, data_type in INPUT_MAP:
            add_input(key, data_type, input_json, product_dict)
    except Exception as e:
        return str(e)

    db = get_database()

    product_id = str(uuid.uuid4())
    product_dict["product_id"] = product_id
    db[PRODUCTS_COL].insert_one(product_dict)

    search_handler.add_product(product_id, product_dict)
    return jsonify({"success": product_id}), 200


def add_input(key, data_type, input_dict, output_dict):
    if key not in input_dict or len(str(input_dict[key]).strip()) == 0:
        raise Exception("Missing " + key)

    if data_type == str:
        output_dict[key] = str(input_dict[key])
    elif data_type == int:
        output_dict[key] = int(input_dict[key])
    elif data_type == float:
        output_dict[key] = float(input_dict[key])
