"""Komponent wykonujący requesty HTTP z retry i backoff."""

import time
from collections.abc import Callable
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from infrastructure.http.policies.retry.default import DefaultRetryPolicy
from infrastructure.http.rate_limiter.min_delay import MinDelayRateLimiter


class RequestExecutor:
    """Wykonuje request z retry/backoff/rate-limit."""

    def __init__(
        self,
        *,
        retry_policy: DefaultRetryPolicy,
        rate_limiter: MinDelayRateLimiter,
        sleep_fn: Callable[[float], None] | None = None,
    ) -> None:
        self._retry_policy = retry_policy
        self._rate_limiter = rate_limiter
        self._sleep_fn = sleep_fn or time.sleep

    def execute(
        self,
        *,
        url: str,
        headers: dict[str, str],
        timeout: int,
        request_func: Callable[..., Any],
        request_exception_cls: type[Exception],
    ) -> Any:
        attempts = self._retry_policy.max_retries + 1

        for attempt in range(attempts):
            self._rate_limiter.wait(url)

            try:
                response = request_func(
                    url,
                    headers=headers,
                    timeout=timeout,
                )
            except request_exception_cls as exc:
                if attempt >= self._retry_policy.max_retries or not self._should_retry(
                    response=None,
                    exception=exc,
                    attempt=attempt,
                ):
                    raise
                self._backoff_sleep(attempt)
                continue

            if self._should_retry(
                response=response,
                exception=None,
                attempt=attempt,
            ):
                if attempt >= self._retry_policy.max_retries:
                    response.raise_for_status()
                self._backoff_sleep(attempt)
                continue

            response.raise_for_status()
            return response

        msg = "Unreachable code"
        raise AssertionError(msg)

    def execute_batch(
        self,
        *,
        urls: Iterable[str],
        headers: dict[str, str],
        timeout: int,
        request_func: Callable[..., Any],
        request_exception_cls: type[Exception],
        max_workers: int = 10,
    ) -> list[Any]:
        """
        Wykonuje wiele requestów w sposób współbieżny (batch).
        Pomaga to uniknąć problemu N+1 zapytań dla zapytań sekwencyjnych.
        """

        def _execute_single(url: str) -> Any:
            return self.execute(
                url=url,
                headers=headers,
                timeout=timeout,
                request_func=request_func,
                request_exception_cls=request_exception_cls,
            )

        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            return list(pool.map(_execute_single, urls))

    def _backoff_sleep(self, attempt: int) -> None:
        delay = self._retry_policy.backoff_seconds(attempt)
        if delay > 0:
            self._sleep_fn(delay)

    def _should_retry(
        self,
        *,
        response: Any | None,
        exception: Exception | None,
        attempt: int,
    ) -> bool:
        """Call retry policy with compatibility for legacy signatures."""

        try:
            return self._retry_policy.should_retry(
                response=response,
                exception=exception,
                attempt=attempt,
            )
        except TypeError:
            pass

        try:
            return self._retry_policy.should_retry(
                response=response,
                exception=exception,
                _attempt=attempt,
            )
        except TypeError:
            pass

        try:
            return self._retry_policy.should_retry(
                response=response,
                exception=exception,
            )
        except TypeError:
            return self._retry_policy.should_retry(response, exception, attempt)


__all__ = ["RequestExecutor"]
