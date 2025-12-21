"""Implementacje klientów HTTP (requests i urllib)."""

from __future__ import annotations
import requests
from typing import Dict, Optional

from http_client import requests_shim
from http_client.base import BaseHttpClient
from http_client.policies import RetryPolicy, RateLimiter, ResponseCache


class HttpClient(BaseHttpClient):
    """Klient HTTP (requests) ze współdzieloną sesją, retry, rate-limit i cache."""

    def __init__(
        self,
        *,
        session: Optional[requests.Session] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 10,
        retry_policy: RetryPolicy | None = None,
        rate_limiter: RateLimiter | None = None,
        cache: ResponseCache | None = None,
    ) -> None:
        session = session or requests.Session()

        super().__init__(
            session=session,
            headers=headers,
            timeout=timeout,
            retry_policy=retry_policy,
            rate_limiter=rate_limiter,
            cache=cache,
            request_exception_cls=requests.RequestException,
        )

    def get(
        self,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ):
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
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 10,
        retry_policy: RetryPolicy | None = None,
        rate_limiter: RateLimiter | None = None,
        cache: ResponseCache | None = None,
    ) -> None:
        session = session or requests_shim.Session()

        super().__init__(
            session=session,
            headers=headers,
            timeout=timeout,
            retry_policy=retry_policy,
            rate_limiter=rate_limiter,
            cache=cache,
            request_exception_cls=requests_shim.RequestException,
        )

    def get(
        self,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ):
        return self._request_with_retries(
            url,
            headers=headers,
            timeout=timeout,
            request_func=self.session.get,
        )
