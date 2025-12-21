"""Implementacje klientów HTTP (requests i urllib)."""

from __future__ import annotations

from typing import Dict, Optional

import requests

from infrastructure.http_client import requests_shim
from infrastructure.http_client.base import BaseHttpClient
from infrastructure.http_client.config import HttpClientConfig
from infrastructure.http_client.interfaces import HttpResponseProtocol


class HttpClient(BaseHttpClient):
    """Klient HTTP (requests) ze współdzieloną sesją, retry, rate-limit i cache."""

    def __init__(
        self,
        *,
        session: Optional[requests.Session] = None,
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


class UrllibHttpClient(BaseHttpClient):
    """Klient HTTP oparty o urllib (requests_shim), zgodny z HttpClientProtocol."""

    def __init__(
        self,
        *,
        session: Optional[requests_shim.Session] = None,
        config: HttpClientConfig | None = None,
    ) -> None:
        """
        Inicjalizacja klienta HTTP opartego na urllib.

        Args:
            session: Opcjonalna sesja requests_shim. Jeśli None, tworzona jest nowa.
            config: Konfiguracja klienta. Jeśli None, używane są wartości domyślne.
        """
        super().__init__(
            session=session or requests_shim.Session(),
            config=config or HttpClientConfig(),
            request_exception_cls=requests_shim.RequestException,
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

