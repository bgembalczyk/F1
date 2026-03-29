from collections.abc import Mapping

from infrastructure.http_client.requests_shim.request_error import RequestError


class HttpShimErrorResponseAdapter:
    """Adapter utrzymujący kompatybilność z obiektami typu requests.Response."""

    def __init__(self, error: "HttpShimError") -> None:
        self.url = error.url
        self.status_code = error.status_code
        self.headers = error.headers
        self.text = error.body

    def raise_for_status(self) -> None:
        """Interfejs zgodny z requests.Response; błąd jest już podniesiony."""
        return


class HttpShimError(RequestError):
    """Bazowy błąd HTTP dla requests_shim z polami domenowymi."""

    def __init__(
        self,
        *,
        url: str,
        status_code: int,
        message: str,
        headers: Mapping[str, str],
        body: str,
    ) -> None:
        super().__init__(message)
        self.url = url
        self.status_code = int(status_code)
        self.headers = {str(k): str(v) for k, v in headers.items()}
        self.body = body
        self.response = HttpShimErrorResponseAdapter(self)

