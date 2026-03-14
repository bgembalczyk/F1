import urllib.error
import urllib.request
from urllib.parse import urlsplit

from infrastructure.http_client.requests_shim.constants import SSL_CONTEXT
from infrastructure.http_client.requests_shim.request_exception import RequestException
from infrastructure.http_client.requests_shim.response import Response
from infrastructure.http_client.requests_shim.timeout import Timeout

ALLOWED_URL_SCHEMES = {"http", "https"}


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
            raise RequestException(msg)

        request = urllib.request.Request(url, headers=merged_headers)  # noqa: S310

        try:
            with urllib.request.urlopen(  # noqa: S310
                request,
                timeout=timeout,
                context=SSL_CONTEXT,
            ) as resp:
                body = resp.read()
                status_code = resp.getcode() or 0
                return Response(url, body, status_code, headers=dict(resp.headers))
        except urllib.error.HTTPError as exc:
            body = exc.read() or b""
            response = Response(url, body, exc.code, headers=dict(exc.headers))
            response.raise_for_status()
            return response
        except urllib.error.URLError as exc:
            if isinstance(exc.reason, TimeoutError):
                raise Timeout(str(exc)) from exc
            raise RequestException(str(exc)) from exc
