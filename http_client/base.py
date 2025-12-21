"""Klasa bazowa dla klientów HTTP."""

from __future__ import annotations

import json
import time
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional, cast

from http_client.caching import WikipediaCachePolicy
from http_client.interfaces import HttpClientProtocol
from http_client.policies import RateLimiter, ResponseCache, RetryPolicy
from http_client.rate_limiting import MinDelayRateLimiter
from http_client.retry import DefaultRetryPolicy


class BaseHttpClient(ABC, HttpClientProtocol):
    """Wspólna klasa bazowa dla klientów HTTP."""

    DEFAULT_HEADERS: Dict[str, str] = {
        "User-Agent": "F1Scrapers/1.0 contact: bartosz.gembalczyk.stud@pw.edu.pl ",
        "Accept-Language": "en-US,en;q=0.9",
    }

    def __init__(
        self,
        *,
        session: Any,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 10,
        retry_policy: RetryPolicy | None = None,
        rate_limiter: RateLimiter | None = None,
        cache: ResponseCache | None = None,
        request_exception_cls: type[Exception],
    ) -> None:
        self.session = session
        self.timeout = int(timeout)

        self.retry_policy = retry_policy or DefaultRetryPolicy(
            retries=0,
            backoff_seconds=0.5,
        )
        self.rate_limiter = rate_limiter or MinDelayRateLimiter()

        # Domyślny cache dla Wikipedii (można wyłączyć: cache=None)
        self.cache: ResponseCache | None = cache or WikipediaCachePolicy.with_file_cache()

        self.request_exception_cls = request_exception_cls

        merged_headers = dict(self.DEFAULT_HEADERS)
        if headers:
            merged_headers.update(headers)
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
    ):
        """Pobiera URL i zwraca response."""
        ...

    def get_text(
        self,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> str:
        # Cache jest świadomie *tylko po URL* (headers/timeout pomijamy),
        # bo to typowy use-case: Wikipedia GET.
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
        # Celowo bazuje na get_text(), żeby cache zadziałał również dla JSON.
        return json.loads(self.get_text(url, headers=headers, timeout=timeout))
