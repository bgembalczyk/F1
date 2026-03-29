import urllib.error
import urllib.request
from urllib.parse import urlsplit

from infrastructure.http_client.requests_shim.constants import ALLOWED_URL_SCHEMES
from infrastructure.http_client.requests_shim.constants import SSL_CONTEXT
from infrastructure.http_client.requests_shim.request_error import RequestError
from infrastructure.http_client.requests_shim.response import Response
from infrastructure.http_client.requests_shim.timeout_error import HTTPTimeoutError


class Session:
    def __init__(self) -> None:
        self.headers: dict[str, str] = {}

    def get(
        self,
        url: str,
        headers: dict[str, str] | None = None,
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
                context=SSL_CONTEXT,
            ) as resp:
                body = resp.read()
                status_code = resp.getcode() or 0
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
