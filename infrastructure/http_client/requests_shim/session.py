import urllib.request, urllib.error
from typing import Dict
from typing import Optional

from infrastructure.http_client.requests_shim.request_exception import RequestException
from infrastructure.http_client.requests_shim.response import Response
from infrastructure.http_client.requests_shim.ssl_context import SSL_CONTEXT
from infrastructure.http_client.requests_shim.timeout import Timeout


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
