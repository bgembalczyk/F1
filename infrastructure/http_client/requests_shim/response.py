from infrastructure.http_client.requests_shim.http_error import HTTPError

HTTP_BAD_REQUEST = 400


class Response:
    def __init__(self, url: str, body: bytes, status_code: int, headers=None):
        self.url = url
        self.status_code = status_code
        self.headers = headers or {}
        self.text = body.decode("utf-8", errors="replace")

    def raise_for_status(self) -> None:
        if self.status_code >= HTTP_BAD_REQUEST:
            raise HTTPError(self.url, self.status_code, self.text, self.headers)
