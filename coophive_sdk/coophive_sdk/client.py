import requests
from .queries import Queries


class CoopHiveClient:
    def __init__(self, host='localhost', port=8001):
        self.base_url = f'http://{host}:{port}'
        self.queries = Queries(self)

    def _request(self, method, endpoint, **kwargs):
        url = f'{self.base_url}{endpoint}'
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
