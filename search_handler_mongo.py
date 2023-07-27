from pymongo.database import Database

from search_handler import SearchHandler

PRODUCTS_COL = "products"
INPUT_KEYS = ["name", "description"]


class SearchHandlerMongo(SearchHandler):
    def __init__(self, db: Database) -> None:
        self.db = db

    def add_product(self, product_id, product_dict) -> bool:
        # This shouldn't matter, it should have been added to the db already.
        return True

    def delete_product(self, product_id) -> bool:
        # This shouldn't matter, it should have been deleted from the db already.
        return True

    def get_all(self):
        results = self.db[PRODUCTS_COL].find()
        return [doc["product_id"] for doc in results]

    def search_product(self, search_term):
        results = self.db[PRODUCTS_COL].find({
            "$or": [
                {"name": {"$regex": search_term, '$options': 'i'}},
                {"description": {"$regex": search_term, '$options': 'i'}}
            ]
        })
        return [doc["product_id"] for doc in results]

    def to_string(self):
        return "MongoDB queries"
