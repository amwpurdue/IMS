from elasticsearch import Elasticsearch, exceptions

INPUT_KEYS = ["name", "description"]


class SearchHandler:
    def __init__(self, index_name) -> None:
        self.INDEX_NAME = index_name
        self.es = Elasticsearch(
            cloud_id="ims:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvJDUwZTU2ZTdiMTRhZjQxMzQ4MDZhNTkxZGY1MzBkNTI4JGE3OTczNDM4ZjI5MzQ4NGRhMDA2YTAxMTM2Y2ZiYmJm",
            basic_auth=("elastic", "pRKY6somzlp2xyO3FGPq4yga")
        )

    def add_product(self, product_id, product_dict) -> bool:
        new_product_doc = dict(map(lambda key: (key, product_dict[key]), INPUT_KEYS))

        created_response = self.es.index(index=self.INDEX_NAME, id=product_id, document=new_product_doc)
        return created_response == "created"

    def delete_product(self, product_id) -> bool:
        return self.es.delete(index=self.INDEX_NAME, id=product_id)

    def get_product(self, product_id):
        try:
            return self.es.get(index=self.INDEX_NAME, id=product_id)
        except exceptions.NotFoundError:
            return None

    def get_all(self):
        return self.search({
            'match_all': {}
        })

    def search_product(self, search_term):
        return self.search({
            "simple_query_string": {
                "query": search_term,
                "fields": ["name^5", "description"]
            }
        })

    def search(self, search_query):
        self.es.indices.refresh(index=self.INDEX_NAME)
        search_results = self.es.search(index=self.INDEX_NAME, query=search_query, size=100)
        return [res.get("_id") for res in search_results["hits"]["hits"]]
