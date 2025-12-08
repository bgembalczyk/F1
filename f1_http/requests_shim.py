"""Minimalna implementacja biblioteki `requests` oparta na urllib."""

from __future__ import annotations

import ssl
import urllib.error
import urllib.request
from typing import Dict, Optional

try:  # pragma: no cover - zależne od środowiska
    import certifi
except Exception:  # pragma: no cover - brak optionala
    certifi = None


class RequestException(Exception):
    pass


class HTTPError(RequestException):
    def __init__(self, url: str, status_code: int, message: str, headers=None):
        super().__init__(message)
        self.url = url
        self.status_code = status_code
        self.headers = headers or {}
        # kompatybilność z requests.Response
        self.response = self


class Timeout(RequestException):
    pass


class Response:
    def __init__(self, url: str, body: bytes, status_code: int, headers=None):
        self.url = url
        self.status_code = status_code
        self.headers = headers or {}
        self.text = body.decode("utf-8", errors="replace")

    def raise_for_status(self) -> None:
        if 400 <= self.status_code:
            raise HTTPError(self.url, self.status_code, self.text, self.headers)


# Globalny kontekst SSL z bundlą CA z certifi, jeśli dostępny
if certifi:
    _SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
else:
    _SSL_CONTEXT = ssl.create_default_context()


class Session:
    def __init__(self) -> None:
        self.headers: Dict[str, str] = {}

    def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> Response:
        merged_headers = dict(self.headers)
        if headers:
            merged_headers.update(headers)

        request = urllib.request.Request(url, headers=merged_headers)

        try:
            with urllib.request.urlopen(
                request,
                timeout=timeout,
                context=_SSL_CONTEXT,
            ) as resp:
                body = resp.read()
                status_code = resp.getcode() or 0
                return Response(url, body, status_code, headers=dict(resp.headers))
        except urllib.error.HTTPError as exc:
            body = exc.read() or b""
            response = Response(url, body, exc.code, headers=dict(exc.headers))
            response.raise_for_status()
            return response
        except urllib.error.URLError as exc:  # pragma: no cover - delegacja błędów
            # urllib zwykle używa socket.timeout, ale zostawiamy Twoją logikę
            if isinstance(exc.reason, TimeoutError):
                raise Timeout(str(exc)) from exc
            raise RequestException(str(exc)) from exc
