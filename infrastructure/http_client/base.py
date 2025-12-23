"""Klasa bazowa dla klientów HTTP."""

import json
import time
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional, cast

from infrastructure.http_client.caching import WikipediaCachePolicy
from infrastructure.http_client.config import HttpClientConfig
from infrastructure.http_client.interfaces import HttpResponseProtocol
from infrastructure.http_client.policies import RateLimiter, ResponseCache, RetryPolicy
from infrastructure.http_client.rate_limiting import MinDelayRateLimiter
from infrastructure.http_client.retry import DefaultRetryPolicy


class BaseHttpClient(ABC):
    """Wspólna klasa bazowa dla klientów HTTP."""

    DEFAULT_HEADERS: Dict[str, str] = {
        "User-Agent": "F1Scrapers/1.0 contact: bartosz.gembalczyk.stud@pw.edu.pl ",
        "Accept-Language": "en-US,en;q=0.9",
    }

    def __init__(
        self,
        *,
        session: Any,
        config: HttpClientConfig,
        request_exception_cls: type[Exception],
    ) -> None:
        """
        Inicjalizacja klienta HTTP.

        Args:
            session: Obiekt sesji (requests.Session lub requests_shim.Session)
            config: Konfiguracja klienta HTTP
            request_exception_cls: Klasa wyjątku dla błędów requestów
        """
        self.session = session
        self.config = config
        self.timeout = int(config.timeout)
        self.request_exception_cls = request_exception_cls

        # Buduj retry policy
        if config.retry_policy is None:
            self.retry_policy: RetryPolicy = DefaultRetryPolicy(
                retries=config.retries,
                backoff_seconds=config.backoff_seconds,
            )
        else:
            self.retry_policy = config.retry_policy

        # Buduj rate limiter
        if config.rate_limiter is None:
            self.rate_limiter: RateLimiter = MinDelayRateLimiter(
                min_delay_seconds=config.min_delay_seconds,
                jitter_seconds=config.jitter_seconds,
            )
        else:
            self.rate_limiter = config.rate_limiter

        # Buduj cache
        if config.cache is None:
            self.cache: ResponseCache | None = WikipediaCachePolicy.with_file_cache(
                cache_dir=config.cache_dir,
                ttl_days=config.cache_ttl_days,
            )
        else:
            self.cache = config.cache

        # Merge headers
        merged_headers = dict(self.DEFAULT_HEADERS)
        if config.headers:
            merged_headers.update(config.headers)
        self.default_headers = merged_headers

    def _backoff_sleep(self, attempt: int) -> None:
        delay = self.retry_policy.backoff_seconds(attempt)
        if delay > 0:
            time.sleep(delay)

    def _request_with_retries(
        self,
        url: str,
        *,
        headers: Optional[Dict[str, str]],
        timeout: Optional[int],
        request_func: Callable[..., Any],
    ):
        attempts = self.retry_policy.max_retries + 1

        for attempt in range(attempts):
            if self.rate_limiter is not None:
                self.rate_limiter.wait(url)

            try:
                merged_headers = dict(self.default_headers)
                if headers:
                    merged_headers.update(headers)

                response = request_func(
                    url,
                    headers=merged_headers,
                    timeout=timeout or self.timeout,
                )
            except self.request_exception_cls as exc:
                if (
                    attempt >= self.retry_policy.max_retries
                    or not self.retry_policy.should_retry(
                        response=None,
                        exception=exc,
                        attempt=attempt,
                    )
                ):
                    raise
                self._backoff_sleep(attempt)
                continue

            if self.retry_policy.should_retry(
                response=response,
                exception=None,
                attempt=attempt,
            ):
                if attempt >= self.retry_policy.max_retries:
                    response.raise_for_status()
                self._backoff_sleep(attempt)
                continue

            response.raise_for_status()
            return cast(Any, response)

        assert False, "Unreachable code"

    @abstractmethod
    def get(
        self,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> HttpResponseProtocol:
        """Pobiera URL i zwraca response."""
        ...

    def get_text(
        self,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> str:
        """
        Zwraca response.text z obsługą cache.

        Cache działa tylko po URL (headers/timeout są ignorowane w cache key).
        """
        if self.cache is not None:
            cached = self.cache.get(url)
            if cached is not None:
                return cached

        response = self.get(url, headers=headers, timeout=timeout)
        text = response.text

        if self.cache is not None:
            self.cache.set(url, text)

        return text

    def get_json(
        self,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> Any:
        """
        Parsuje JSON z odpowiedzi.

        Bazuje na get_text(), więc cache działa również dla JSON.
        """
        return json.loads(self.get_text(url, headers=headers, timeout=timeout))
