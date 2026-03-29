from collections.abc import Mapping
import ssl
import socket
import urllib.error
import urllib.request
from urllib.parse import urlsplit

from infrastructure.http_client.requests_shim.constants import ALLOWED_URL_SCHEMES
from infrastructure.http_client.requests_shim.constants import HTTP_STATUS_UNKNOWN
from infrastructure.http_client.requests_shim.constants import SSL_CONTEXT
from infrastructure.http_client.requests_shim.request_error import RequestError
from infrastructure.http_client.requests_shim.response import Response
from infrastructure.http_client.requests_shim.ssl import SSLContextProvider
from infrastructure.http_client.requests_shim.ssl import build_ssl_context
from infrastructure.http_client.requests_shim.timeout_error import HTTPTimeoutError


class Session:
    def __init__(
        self,
        *,
        ssl_context: ssl.SSLContext | None = None,
        ssl_context_provider: SSLContextProvider | None = None,
    ) -> None:
        self.headers: dict[str, str] = {}
        provider = ssl_context_provider or build_ssl_context
        self._ssl_context = ssl_context or provider()

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
        if parsed_url.scheme not in ALLOWED_URL_SCHEMES:
            msg = f"Unsupported URL scheme: {parsed_url.scheme!r}"
            raise RequestError(msg)

        request = urllib.request.Request(url, headers=merged_headers)  # noqa: S310

        try:
            with urllib.request.urlopen(  # noqa: S310
                request,
                timeout=timeout,
                context=self._ssl_context,
            ) as resp:
                body = resp.read()
                status_code = resp.getcode() or HTTP_STATUS_UNKNOWN
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
            if isinstance(exc.reason, TimeoutError | socket.timeout):
                detail = str(exc.reason or exc)
                raise HTTPTimeoutError(
                    url=url,
                    message=f"Request timed out: {detail}",
                    headers={},
                    body=detail,
                ) from exc
            raise RequestError(str(exc)) from exc
