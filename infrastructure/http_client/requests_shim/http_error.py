from infrastructure.http_client.requests_shim.request_exception import RequestException


class HTTPError(RequestException):
    def __init__(self, url: str, status_code: int, message: str, headers=None):
        super().__init__(message)
        self.url = url
        self.status_code = status_code
        self.headers = headers or {}
        # kompatybilność z requests.Response
        self.response = self
