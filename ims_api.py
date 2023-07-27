import html
import os
import uuid

from flask import Blueprint, request, jsonify
from pymongo import MongoClient

from search_handler_elastic import SearchHandlerElastic
from search_handler_mongo import SearchHandlerMongo, PRODUCTS_COL

products_page = Blueprint("products_page", __name__, url_prefix="/products")

INPUT_MAP = [
    ("name", str),
    ("category", str),
    ("price", float),
    ("quantity", int),
    ("description", str)
]

PROJECT_DICT = {
    "product_id": 1,
    "name": 1,
    "category": 1,
    "price": 1,
    "description": 1,
    "quantity": 1,
    "sold": 1,
    "quantity_remaining": {
        "$subtract": ["$quantity", "$sold"]
    }
}

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


def get_database():
    return client[os.environ["db_name"]]


if "elastic_cloud_id" in os.environ and "elastic_user_password" in os.environ:
    try:
        search_handler = SearchHandlerElastic(
            os.environ.get("es_index", "search-ims-test"),
            os.environ["elastic_cloud_id"],
            os.environ["elastic_user_password"]
        )
    except Exception as e:
        print("Error in connecting to ElasticSearch: " + str(e))
        search_handler = SearchHandlerMongo(get_database())
else:
    search_handler = SearchHandlerMongo(get_database())


def mongo_product_to_dict(db_result):
    if db_result is None:
        return None

    fields = ["product_id"] + [x for x in PROJECT_DICT]
    return dict([(key, db_result[key]) for key in fields])


@products_page.route("/", methods=["GET"])
def get_products():
    product_list = all_products({})
    return jsonify({"products": product_list}), 200


def all_products(find_dict=None):
    if find_dict is None:
        find_dict = {"$expr": {"$gt": ["$quantity", "$sold"]}}
    db = get_database()

    find_result = db[PRODUCTS_COL].aggregate([
        {"$match": find_dict},
        {"$project": PROJECT_DICT}
    ])

    product_list = []
    for p in find_result:
        product_list.append(mongo_product_to_dict(p))
    return product_list


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
    product = get_product_by_id(product_id)
    if product is not None:
        return jsonify(product), 200

    return jsonify({"error": product_id + " not found"}), 404


def get_product_by_id(product_id):
    db = get_database()

    product_result = db[PRODUCTS_COL].aggregate([
        {"$match": {"product_id": product_id}},
        {"$project": PROJECT_DICT}
    ])
    for x in product_result:
        return mongo_product_to_dict(x)

    return None


@products_page.route("/<product_id>/", methods=["PUT"])
def update_product(product_id):
    if request.headers.get('Content-Type') != 'application/json':
        return jsonify({"error": "json content-type required"}), 400

    product_dict = dict()
    try:
        for key, data_type in INPUT_MAP:
            add_input(key, data_type, request.json, product_dict, optional=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    db = get_database()

    update_response = db[PRODUCTS_COL].update_one(
        {"product_id": product_id},
        {"$set": product_dict}
    )
    if update_response.modified_count == 1:
        updated_product = get_product_by_id(product_id)
        search_handler.delete_product(product_id)
        search_handler.add_product(product_id, updated_product)
        return jsonify({"success": product_id, "product": updated_product}), 200

    return jsonify({"error": update_response}), 500


@products_page.route("/<product_id>/", methods=["DELETE"])
def delete_product(product_id):
    db = get_database()

    db[PRODUCTS_COL].delete_one({"product_id": product_id})
    search_handler.delete_product(product_id)
    return jsonify({"success": product_id}), 200


@products_page.route("/buy/<product_id>/", methods=["POST"])
def buy_product(product_id):
    db = get_database()
    update_response = db[PRODUCTS_COL].update_one(
        {"product_id": product_id},
        {"$inc": {"sold": 1}}
    )
    if update_response.modified_count == 1:
        return jsonify({"success": product_id, "product": get_product_by_id(product_id)}), 200

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
    if "keywords" not in request.args:
        return get_products()

    keywords = request.args.get("keywords")
    product_list = get_products_with_keywords(keywords)
    return jsonify({"products": product_list}), 200


def get_products_with_keywords(keywords):
    db = get_database()
    db["searches"].update_one(
        {"keywords": keywords},
        {"$set": {"keywords": keywords}, "$inc": {"times": 1}},
        upsert=True
    )

    product_list = []
    for res in search_handler.search_product(keywords):
        p = get_product_by_id(res)
        if p is not None:
            product_list.append(p)
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
        return jsonify({"error": str(e)}), 400

    db = get_database()

    product_id = str(uuid.uuid4())
    product_dict["product_id"] = product_id
    product_dict["sold"] = 0
    db[PRODUCTS_COL].insert_one(product_dict)

    search_handler.add_product(product_id, product_dict)
    return jsonify({"success": product_id}), 200


def add_input(key, data_type, input_dict, output_dict, optional=False):
    if key not in input_dict or len(str(input_dict[key]).strip()) == 0:
        if optional:
            return
        raise Exception("Missing " + key)

    if data_type == str:
        output_dict[key] = html.escape(str(input_dict[key]))
    elif data_type == int:
        output_dict[key] = int(input_dict[key])
    elif data_type == float:
        output_dict[key] = float(input_dict[key])


@products_page.route("/analytics", methods=["GET"])
def get_analytics():
    db = get_database()

    new_dict = dict(PROJECT_DICT)
    new_dict.update({
        "revenue": {
            "$multiply": ["$sold", "$price"]
        }
    })
    category_totals = db[PRODUCTS_COL].aggregate([{
        "$project": new_dict
    }, {
        "$group": {
            "_id": "$category",
            "sold": {"$sum": "$sold"},
            "revenue": {"$sum": "$revenue"}
        }
    }, {
        "$project": {
            "sold": 1,
            "revenue": 1,
            "average_sale_price": {
                "$divide": ["$revenue", "$sold"]
            }
        }
    }, {
        "$sort": {"sold": -1}
    }])

    return jsonify({"category_totals": list(category_totals)})
