class Queries:
    def __init__(self, client):
        self.client = client

    def query_database(self, collection_name, user_query):
        data = {
            "user_query": user_query
        }

        return self.client._request('POST', f'/collections/{collection_name}/query', json=data)
