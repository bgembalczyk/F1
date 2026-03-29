"""Klasa bazowa dla klientów HTTP."""

import json
import time
from abc import ABC
from abc import abstractmethod
from collections.abc import Callable
from typing import TYPE_CHECKING
from typing import Any
from typing import cast

from infrastructure.http_client.caching.wiki import WikipediaCachePolicy
from infrastructure.http_client.config import HttpClientConfig
from infrastructure.http_client.interfaces.http_response_protocol import (
    HttpResponseProtocol,
)
from infrastructure.http_client.policies.default_retry import DefaultRetryPolicy
from infrastructure.http_client.policies.min_delay_rate_limiter import (
    MinDelayRateLimiter,
)

if TYPE_CHECKING:
    from infrastructure.http_client.policies.rate_limiter import RateLimiter
    from infrastructure.http_client.policies.response_cache import ResponseCache
    from infrastructure.http_client.policies.retry import RetryPolicy


class BaseHttpClient(ABC):
    """Wspólna klasa bazowa dla klientów HTTP."""

    DEFAULT_HEADERS: dict[str, str] = {
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

    def _merge_request_headers(
        self,
        headers: dict[str, str] | None = None,
    ) -> dict[str, str]:
        """
        Buduje nagłówki requestu wg jawnego kontraktu priorytetu.

        Kontrakt: client > session.
        - session.headers: globalne nagłówki sesji (najniższy priorytet)
        - default_headers klienta + config.headers (wyższy priorytet)
        - headers requestu (najwyższy priorytet)
        """
        merged_headers: dict[str, str] = {}

        session_headers = getattr(self.session, "headers", None)
        if session_headers:
            merged_headers.update(session_headers)

        merged_headers.update(self.default_headers)

        if headers:
            merged_headers.update(headers)
        return merged_headers

    def _backoff_sleep(self, attempt: int) -> None:
        delay = self.retry_policy.backoff_seconds(attempt)
        if delay > 0:
            time.sleep(delay)

    def _request_with_retries(
        self,
        url: str,
        *,
        headers: dict[str, str] | None,
        timeout: int | None,
        request_func: Callable[..., Any],
    ):
        attempts = self.retry_policy.max_retries + 1

        for attempt in range(attempts):
            if self.rate_limiter is not None:
                self.rate_limiter.wait(url)

            try:
                response = request_func(
                    url,
                    headers=self._merge_request_headers(headers),
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
            return cast("Any", response)

        msg = "Unreachable code"
        raise AssertionError(msg)

    @abstractmethod
    def get(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        timeout: int | None = None,
    ) -> HttpResponseProtocol:
        """Pobiera URL i zwraca response."""
        ...

    def get_text(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        timeout: int | None = None,
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
        headers: dict[str, str] | None = None,
        timeout: int | None = None,
    ) -> Any:
        """
        Parsuje JSON z odpowiedzi.

        Bazuje na get_text(), więc cache działa również dla JSON.
        """
        return json.loads(self.get_text(url, headers=headers, timeout=timeout))
