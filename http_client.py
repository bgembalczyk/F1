from __future__ import annotations

import importlib
import time
from typing import Dict, Optional

from f1_http import requests_shim
from f1_http.interfaces import HttpClientProtocol, HttpResponseProtocol

try:  # pragma: no cover - zależne od środowiska
    requests = importlib.import_module("requests")
except Exception:  # pragma: no cover - fallback, gdy brak dependency
    from f1_http import requests_shim as requests  # type: ignore


class HttpClient(HttpClientProtocol):
    """Wspólny klient HTTP ze współdzieloną sesją i domyślnymi nagłówkami."""

    DEFAULT_HEADERS: Dict[str, str] = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/18.0 Safari/605.1.15"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }

    def __init__(
        self,
        *,
        session: Optional[requests.Session] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 10,
        retries: int = 0,
        backoff_seconds: float = 0.5,
    ) -> None:
        self.session = session or requests.Session()
        merged_headers = dict(self.DEFAULT_HEADERS)
        if headers:
            merged_headers.update(headers)
        self.session.headers.update(merged_headers)

        self.timeout = timeout
        self.retries = max(0, retries)
        self.backoff_seconds = backoff_seconds

    def get(
        self,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> HttpResponseProtocol:
        attempts = self.retries + 1
        for attempt in range(attempts):
            try:
                response = self.session.get(
                    url, headers=headers, timeout=timeout or self.timeout
                )
                response.raise_for_status()
                return response
            except requests.RequestException:
                if attempt >= self.retries:
                    raise
                time.sleep(self.backoff_seconds * (attempt + 1))

    def get_text(
        self,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> str:
        response = self.get(url, headers=headers, timeout=timeout)
        return response.text


class UrllibHttpClient(HttpClientProtocol):
    """Lekka implementacja HTTP bazująca na urllib (requests_shim)."""

    def __init__(
        self,
        *,
        session: Optional[requests_shim.Session] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 10,
        retries: int = 0,
        backoff_seconds: float = 0.5,
    ) -> None:
        self.session = session or requests_shim.Session()
        merged_headers = dict(HttpClient.DEFAULT_HEADERS)
        if headers:
            merged_headers.update(headers)
        self.session.headers.update(merged_headers)

        self.timeout = timeout
        self.retries = max(0, retries)
        self.backoff_seconds = backoff_seconds

    def get(
        self,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> HttpResponseProtocol:
        attempts = self.retries + 1
        for attempt in range(attempts):
            try:
                response = self.session.get(
                    url, headers=headers, timeout=timeout or self.timeout
                )
                response.raise_for_status()
                return response
            except requests_shim.RequestException:
                if attempt >= self.retries:
                    raise
                time.sleep(self.backoff_seconds * (attempt + 1))

    def get_text(
        self,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> str:
        response = self.get(url, headers=headers, timeout=timeout)
        return response.text
