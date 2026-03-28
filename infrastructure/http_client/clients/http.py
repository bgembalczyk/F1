import requests

from infrastructure.http_client.clients.base import BaseHttpClient
from infrastructure.http_client.config import HttpClientConfig
from infrastructure.http_client.interfaces.http_response_protocol import (
    HttpResponseProtocol,
)


class HttpClient(BaseHttpClient):
    """Klient HTTP (requests) ze współdzieloną sesją, retry, rate-limit i cache."""

    def __init__(
        self,
        *,
        session: requests.Session | None = None,
        config: HttpClientConfig | None = None,
    ) -> None:
        """
        Inicjalizacja klienta HTTP opartego na requests.

        Args:
            session: Opcjonalna sesja requests. Jeśli None, tworzona jest nowa.
            config: Konfiguracja klienta. Jeśli None, używane są wartości domyślne.
        """
        super().__init__(
            session=session or requests.Session(),
            config=config or HttpClientConfig(),
            request_exception_cls=requests.RequestException,
        )

    def get(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        timeout: int | None = None,
    ) -> HttpResponseProtocol:
        """Wykonuje żądanie GET."""
        return self._request_with_retries(
            url,
            headers=headers,
            timeout=timeout,
            request_func=self.session.get,
        )
