from elasticsearch import Elasticsearch, exceptions

from search_handler import SearchHandler

INPUT_KEYS = ["name", "description"]


class SearchHandlerElastic(SearchHandler):
    def __init__(self, index_name, cloud_id, elastic_password) -> None:
        self.INDEX_NAME = index_name
        self.es = Elasticsearch(
            cloud_id=cloud_id,
            basic_auth=("elastic", elastic_password)
        )

    def add_product(self, product_id, product_dict) -> bool:
        new_product_doc = dict(map(lambda key: (key, product_dict[key]), INPUT_KEYS))

        created_response = self.es.index(index=self.INDEX_NAME, id=product_id, document=new_product_doc)
        return created_response == "created"

    def delete_product(self, product_id) -> bool:
        return self.es.delete(index=self.INDEX_NAME, id=product_id)

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

    def to_string(self):
        return "ElasticSearch Cloud API"
