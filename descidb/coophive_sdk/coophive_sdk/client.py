import requests

from .queries import Queries


class CoopHiveClient:
    def __init__(self, host="localhost", port=8001, api_key=None):
        self.base_url = f"http://{host}:{port}"
        self.api_key = api_key
        self.queries = Queries(self)

    def _request(self, method, endpoint, **kwargs):
        url = f"{self.base_url}{endpoint}"
        headers = kwargs.get("headers", {})
        if self.api_key:
            headers["X-API-KEY"] = self.api_key
        kwargs["headers"] = headers

        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
