"""Implementacje klientów HTTP (requests i urllib)."""

from __future__ import annotations
import requests
from pathlib import Path
from typing import Dict, Optional

from http_client import requests_shim
from http_client.base import BaseHttpClient
from http_client.caching import WikipediaCachePolicy
from http_client.policies import RetryPolicy, RateLimiter, ResponseCache
from http_client.rate_limiting import MinDelayRateLimiter
from http_client.retry import DefaultRetryPolicy


class HttpClient(BaseHttpClient):
    """Klient HTTP (requests) ze współdzieloną sesją, retry, rate-limit i cache."""

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
        retry_policy: RetryPolicy | None = None,
        rate_limiter: RateLimiter | None = None,
        cache: ResponseCache | None = None,
        cache_dir: Path | str | None = None,
        cache_ttl_days: int = 30,
    ) -> None:
        session = session or requests.Session()

        if retry_policy is None:
            retry_policy = DefaultRetryPolicy(
                retries=retries, backoff_seconds=backoff_seconds
            )

        if rate_limiter is None:
            rate_limiter = MinDelayRateLimiter(
                min_delay_seconds=min_delay_seconds,
                jitter_seconds=jitter_seconds,
            )

        super().__init__(
            session=session,
            headers=headers,
            timeout=timeout,
            retry_policy=retry_policy,
            rate_limiter=rate_limiter,
            request_exception_cls=requests.RequestException,
        )

        self.cache = cache or WikipediaCachePolicy.with_file_cache(
            cache_dir=cache_dir,
            ttl_days=cache_ttl_days,
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

    def get_text(
        self,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> str:
        if self.cache is not None:
            cached = self.cache.get(url)
            if cached is not None:
                return cached

        response = self.get(url, headers=headers, timeout=timeout)
        text = response.text

        if self.cache is not None:
            self.cache.set(url, text)

        return text


class UrllibHttpClient(BaseHttpClient):
    """Klient HTTP oparty o urllib (requests_shim), zgodny z HttpClientProtocol."""

    def __init__(
        self,
        *,
        session: Optional[requests_shim.Session] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 10,
        retries: int = 0,
        backoff_seconds: float = 0.5,
        min_delay_seconds: float = 1.5,
        jitter_seconds: float = 0.7,
        retry_policy: RetryPolicy | None = None,
        rate_limiter: RateLimiter | None = None,
        cache: ResponseCache | None = None,
        cache_dir: Path | str | None = None,
        cache_ttl_days: int = 30,
    ) -> None:
        session = session or requests_shim.Session()

        if retry_policy is None:
            retry_policy = DefaultRetryPolicy(
                retries=retries, backoff_seconds=backoff_seconds
            )

        if rate_limiter is None:
            rate_limiter = MinDelayRateLimiter(
                min_delay_seconds=min_delay_seconds,
                jitter_seconds=jitter_seconds,
            )

        super().__init__(
            session=session,
            headers=headers,
            timeout=timeout,
            retry_policy=retry_policy,
            rate_limiter=rate_limiter,
            request_exception_cls=requests_shim.RequestException,
        )

        self.cache = cache or WikipediaCachePolicy.with_file_cache(
            cache_dir=cache_dir,
            ttl_days=cache_ttl_days,
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

    def get_text(
        self,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> str:
        if self.cache is not None:
            cached = self.cache.get(url)
            if cached is not None:
                return cached

        response = self.get(url, headers=headers, timeout=timeout)
        text = response.text

        if self.cache is not None:
            self.cache.set(url, text)

        return text

