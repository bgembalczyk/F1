from infrastructure.http_client.requests_shim.http_error import HTTPError


class Response:
    def __init__(self, url: str, body: bytes, status_code: int, headers=None):
        self.url = url
        self.status_code = status_code
        self.headers = headers or {}
        self.text = body.decode("utf-8", errors="replace")

    def raise_for_status(self) -> None:
        if 400 <= self.status_code:
            raise HTTPError(self.url, self.status_code, self.text, self.headers)
