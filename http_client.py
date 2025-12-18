from __future__ import annotations

import importlib
import random
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, cast

from f1_http import requests_shim
from f1_http.interfaces import HttpClientProtocol, HttpResponseProtocol

try:  # pragma: no cover - zależne od środowiska
    requests = importlib.import_module("requests")
except Exception:  # pragma: no cover - fallback, gdy brak dependency
    from f1_http import requests_shim as requests  # type: ignore


class BaseHttpClient(ABC, HttpClientProtocol):
    """Wspólna klasa bazowa dla klientów HTTP."""

    DEFAULT_HEADERS: Dict[str, str] = {
        "User-Agent": (
            "F1Scrapers/1.0 "
            "contact: bartosz.gembalczyk.stud@pw.edu.pl "
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }

    def __init__(
        self,
        *,
        session: Any = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 10,
        retries: int = 0,
        backoff_seconds: float = 0.5,
        min_delay_seconds: float = 1.5,
        jitter_seconds: float = 0.7,
    ) -> None:
        self.session = session
        self.timeout = timeout
        self.retries = max(0, int(retries))
        self.backoff_seconds = float(backoff_seconds)

        # globalne ograniczanie tempa (per client)
        self.min_delay_seconds = max(0.0, float(min_delay_seconds))
        self.jitter_seconds = max(0.0, float(jitter_seconds))
        self._last_request_ts: float = 0.0

        # Merging headers
        merged_headers = dict(self.DEFAULT_HEADERS)
        if headers:
            merged_headers.update(headers)

        # session.headers może nie istnieć w niektórych shimach — zabezpieczenie
        if getattr(self.session, "headers", None) is not None:
            self.session.headers.update(merged_headers)

    def _sleep_if_needed(self) -> None:
        """Wymusza minimalny odstęp + jitter między requestami."""
        now = time.monotonic()
        elapsed = now - self._last_request_ts
        delay = self.min_delay_seconds - elapsed
        if delay > 0:
            time.sleep(delay + random.random() * self.jitter_seconds)

    def _note_request_made(self) -> None:
        self._last_request_ts = time.monotonic()

    def _backoff_sleep(self, attempt: int) -> None:
        """
        Exponential backoff + jitter.
        attempt: 0..retries-1
        """
        base = self.backoff_seconds * (2 ** attempt)
        time.sleep(base + random.random())

    def _should_retry_status(self, status_code: int, body_text: str) -> bool:
        if status_code in {429, 502, 503, 504}:
            return True
        # Wikipedia potrafi zwracać 403 z tekstem o robot policy / too many requests
        if status_code == 403:
            t = (body_text or "").lower()
            if "too many requests" in t or "robot policy" in t or "please respect our robot policy" in t:
                return True
        return False

    @abstractmethod
    def get(
        self,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ):
        """Pobiera URL i zwraca response."""
        ...

    def get_text(
        self,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> str:
        response = self.get(url, headers=headers, timeout=timeout)
        return response.text


class HttpClient(BaseHttpClient):
    """Klient HTTP ze współdzieloną sesją i domyślnymi nagłówkami."""

    def __init__(
        self,
        *,
        session: Optional[requests.Session] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 10,
        retries: int = 0,
        backoff_seconds: float = 0.5,
        min_delay_seconds: float = 1.5,
        jitter_seconds: float = 0.7,
    ) -> None:
        session = session or requests.Session()
        super().__init__(
            session=session,
            headers=headers,
            timeout=timeout,
            retries=retries,
            backoff_seconds=backoff_seconds,
            min_delay_seconds=min_delay_seconds,
            jitter_seconds=jitter_seconds,
        )

    def get(
        self,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ):
        attempts = self.retries + 1

        for attempt in range(attempts):
            self._sleep_if_needed()
            try:
                response = self.session.get(
                    url,
                    headers=headers,
                    timeout=timeout or self.timeout,
                )
                self._note_request_made()

                # ręczna obsługa “rate limit” / chwilowych błędów
                status = int(getattr(response, "status_code", 0) or 0)
                if status and self._should_retry_status(status, getattr(response, "text", "")):
                    if attempt >= self.retries:
                        response.raise_for_status()
                    self._backoff_sleep(attempt)
                    continue

                response.raise_for_status()
                return cast(Any, response)

            except requests.RequestException:
                self._note_request_made()
                if attempt >= self.retries:
                    raise
                self._backoff_sleep(attempt)

        assert False, "Unreachable code"

