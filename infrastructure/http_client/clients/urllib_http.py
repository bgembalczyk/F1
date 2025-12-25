from typing import Dict
from typing import Optional

from infrastructure.http_client.clients.base import BaseHttpClient
from infrastructure.http_client.config import HttpClientConfig
from infrastructure.http_client.interfaces.http_response_protocol import (
    HttpResponseProtocol,
)
from infrastructure.http_client.requests_shim.request_exception import RequestException
from infrastructure.http_client.requests_shim.session import Session


class UrllibHttpClient(BaseHttpClient):
    """Klient HTTP oparty o urllib (requests_shim), zgodny z HttpClientProtocol."""

    def __init__(
        self,
        *,
        session: Optional[Session] = None,
        config: HttpClientConfig | None = None,
    ) -> None:
        """
        Inicjalizacja klienta HTTP opartego na urllib.

        Args:
            session: Opcjonalna sesja requests_shim. Jeśli None, tworzona jest nowa.
            config: Konfiguracja klienta. Jeśli None, używane są wartości domyślne.
        """
        super().__init__(
            session=session or Session(),
            config=config or HttpClientConfig(),
            request_exception_cls=RequestException,
        )

    def get(
        self,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> HttpResponseProtocol:
        """Wykonuje żądanie GET."""
        return self._request_with_retries(
            url,
            headers=headers,
            timeout=timeout,
            request_func=self.session.get,
        )
