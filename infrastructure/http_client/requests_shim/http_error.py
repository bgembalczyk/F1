from collections.abc import Mapping

from infrastructure.http_client.requests_shim.http_shim_error import HttpShimError


class HTTPError(HttpShimError):
    """Błąd odpowiedzi HTTP (status >= 400)."""

    def __init__(
        self,
        url: str,
        status_code: int,
        message: str,
        headers: Mapping[str, str],
        body: str,
    ) -> None:
        super().__init__(
            url=url,
            status_code=status_code,
            message=message,
            headers=headers,
            body=body,
        )
