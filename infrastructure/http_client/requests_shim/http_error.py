from infrastructure.http_client.requests_shim.request_error import RequestError


class HTTPError(RequestError):
    def __init__(self, url: str, status_code: int, message: str, headers=None):
        super().__init__(
            message,
            url=url,
            status=status_code,
            headers=headers,
        )
        # kompatybilność z requests.Response
        self.response = self
