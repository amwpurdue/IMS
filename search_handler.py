from elasticsearch import Elasticsearch, exceptions


class SearchHandler:
    def __init__(self, index_name) -> None:
        self.INDEX_NAME = index_name
        self.es = Elasticsearch(
            cloud_id="ims:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvJDUwZTU2ZTdiMTRhZjQxMzQ4MDZhNTkxZGY1MzBkNTI4JGE3OTczNDM4ZjI5MzQ4NGRhMDA2YTAxMTM2Y2ZiYmJm",
            basic_auth=("elastic", "pRKY6somzlp2xyO3FGPq4yga")
        )

    def add_product(self, product_id, product_name, product_description) -> bool:
        new_product_doc = {
            "name": product_name,
            "description": product_description
        }
        created_response = self.es.index(index=self.INDEX_NAME, id=product_id, document=new_product_doc)
        print("created_response: ")
        print(created_response)
        return created_response == "created"

    def get_product(self, product_id):
        try:
            return self.es.get(index=self.INDEX_NAME, id=product_id)
        except exceptions.NotFoundError:
            return None

    def search_product(self, search_term):
        self.es.indices.refresh(index=self.INDEX_NAME)
        query = {
            "combined_fields": {
                "query": search_term,
                "fields": ["name^5", "description"]
            }
        }
        search_results = self.es.search(index=self.INDEX_NAME, query=query)
        return [res.get("_id") for res in search_results["hits"]["hits"]]
