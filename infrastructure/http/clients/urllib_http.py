from collections.abc import Mapping

from infrastructure.http.clients.base import BaseHttpClient
from infrastructure.http.config import HttpClientConfig
from infrastructure.http.errors.base import RequestError
from infrastructure.http.protocols.response import HttpResponseProtocol
from infrastructure.http.protocols.session import SessionProtocol
from infrastructure.http.session import Session


class UrllibHttpClient(BaseHttpClient):
    """Klient HTTP oparty o urllib (requests_shim), zgodny z HttpClientProtocol."""

    def __init__(
        self,
        *,
        session: SessionProtocol | None = None,
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
            request_exception_cls=RequestError,
        )

    def get(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        timeout: int | None = None,
    ) -> HttpResponseProtocol:
        """Wykonuje żądanie GET."""
        return self._request_with_retries(
            url,
            headers=headers,
            timeout=timeout,
            request_func=self.session.get,
        )
