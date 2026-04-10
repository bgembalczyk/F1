from collections.abc import Mapping

from infrastructure.http.errors.base import RequestError
from infrastructure.http.errors.shim.response_adapter import (
    HttpShimErrorResponseAdapter,
)


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


__all__ = ["HttpShimError"]
