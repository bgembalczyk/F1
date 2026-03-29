from collections.abc import Mapping

from infrastructure.http_client.requests_shim.http_shim_error import HttpShimError


class HTTPTimeoutError(HttpShimError):
    """Błąd timeoutu HTTP (brak odpowiedzi w wymaganym czasie)."""

    def __init__(
        self,
        *,
        url: str,
        message: str,
        headers: Mapping[str, str],
        body: str,
        status_code: int = 0,
    ) -> None:
        super().__init__(
            url=url,
            status_code=status_code,
            message=message,
            headers=headers,
            body=body,
        )
