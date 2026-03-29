from collections.abc import Mapping
import ssl
import urllib.error
import urllib.request
from urllib.parse import urlsplit

import certifi

from infrastructure.http_client.requests_shim import constants as shim_constants
from infrastructure.http_client.requests_shim.request_error import RequestError
from infrastructure.http_client.requests_shim.response import Response
from infrastructure.http_client.requests_shim.timeout_error import HTTPTimeoutError


def _resolve_ssl_context() -> ssl.SSLContext:
    """Zwraca kontekst SSL z constants, a awaryjnie tworzy nowy."""
    configured_context = getattr(shim_constants, "SSL_CONTEXT", None)
    if configured_context is not None:
        return configured_context
    return ssl.create_default_context(cafile=certifi.where())


class Session:
    def __init__(self) -> None:
        self.headers: dict[str, str] = {}

    def get(
        self,
        url: str,
        headers: Mapping[str, str] | None = None,
        timeout: int | None = None,
    ) -> Response:
        merged_headers = dict(self.headers)
        if headers:
            merged_headers.update(headers)

        parsed_url = urlsplit(url)
        if parsed_url.scheme not in shim_constants.ALLOWED_URL_SCHEMES:
            msg = f"Unsupported URL scheme: {parsed_url.scheme!r}"
            raise RequestError(msg)

        request = urllib.request.Request(url, headers=merged_headers)  # noqa: S310

        try:
            with urllib.request.urlopen(  # noqa: S310
                request,
                timeout=timeout,
                context=_resolve_ssl_context(),
            ) as resp:
                body = resp.read()
                status_code = resp.getcode() or shim_constants.HTTP_STATUS_UNKNOWN
                text = body.decode("utf-8", errors="replace")
                return Response(url=url, status_code=status_code, headers=resp.headers, text=text)
        except urllib.error.HTTPError as exc:
            body = exc.read() or b""
            text = body.decode("utf-8", errors="replace")
            response = Response(
                url=url,
                status_code=exc.code,
                headers=exc.headers,
                text=text,
            )
            response.raise_for_status()
            return response
        except urllib.error.URLError as exc:
            if isinstance(exc.reason, HTTPTimeoutError):
                raise HTTPTimeoutError(str(exc)) from exc
            raise RequestError(str(exc)) from exc
