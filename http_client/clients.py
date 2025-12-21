"""Implementacje klientów HTTP (requests i urllib)."""

from __future__ import annotations

import warnings
from dataclasses import replace
from pathlib import Path
from typing import Dict, Optional

import requests

from http_client import requests_shim
from http_client.base import BaseHttpClient
from http_client.caching import WikipediaCachePolicy
from http_client.config import HttpClientConfig
from http_client.interfaces import HttpResponseProtocol
from http_client.policies import RateLimiter, ResponseCache, RetryPolicy
from http_client.rate_limiting import MinDelayRateLimiter
from http_client.retry import DefaultRetryPolicy


def _resolve_config(
    config: HttpClientConfig | None,
    *,
    headers: Optional[Dict[str, str]],
    timeout: int | None,
    retries: int | None,
    backoff_seconds: float | None,
    min_delay_seconds: float | None,
    jitter_seconds: float | None,
    retry_policy: RetryPolicy | None,
    rate_limiter: RateLimiter | None,
    cache: ResponseCache | None,
    cache_dir: Path | str | None,
    cache_ttl_days: int | None,
) -> HttpClientConfig:
    legacy_used = any(
        value is not None
        for value in (
            headers,
            timeout,
            retries,
            backoff_seconds,
            min_delay_seconds,
            jitter_seconds,
            retry_policy,
            rate_limiter,
            cache,
            cache_dir,
            cache_ttl_days,
        )
    )

    if config is None:
        config = HttpClientConfig()

    if legacy_used:
        warnings.warn(
            "Parametry konfiguracyjne klienta HTTP przekazuj przez HttpClientConfig.",
            DeprecationWarning,
            stacklevel=3,
        )

    overrides: dict[str, object] = {}
    if headers is not None:
        overrides["headers"] = headers
    if timeout is not None:
        overrides["timeout"] = timeout
    if retries is not None:
        overrides["retries"] = retries
    if backoff_seconds is not None:
        overrides["backoff_seconds"] = backoff_seconds
    if min_delay_seconds is not None:
        overrides["min_delay_seconds"] = min_delay_seconds
    if jitter_seconds is not None:
        overrides["jitter_seconds"] = jitter_seconds
    if retry_policy is not None:
        overrides["retry_policy"] = retry_policy
    if rate_limiter is not None:
        overrides["rate_limiter"] = rate_limiter
    if cache is not None:
        overrides["cache"] = cache
    if cache_dir is not None:
        overrides["cache_dir"] = cache_dir
    if cache_ttl_days is not None:
        overrides["cache_ttl_days"] = cache_ttl_days

    if overrides:
        config = replace(config, **overrides)

    return config


def _build_effective_policies(
    config: HttpClientConfig,
) -> tuple[RetryPolicy, RateLimiter, ResponseCache | None]:
    """
    Buduje retry/rate-limit/cache w stylu `main`, ale z wartościami z HttpClientConfig.

    Zasada:
    - jeśli w config jest jawnie ustawione retry_policy / rate_limiter / cache -> używamy tego,
    - w przeciwnym razie tworzymy domyślne implementacje (DefaultRetryPolicy, MinDelayRateLimiter,
      WikipediaCachePolicy.with_file_cache()).
    """
    if config.retry_policy is None:
        retry_policy: RetryPolicy = DefaultRetryPolicy(
            retries=config.retries,
            backoff_seconds=config.backoff_seconds,
        )
    else:
        retry_policy = config.retry_policy

    if config.rate_limiter is None:
        rate_limiter: RateLimiter = MinDelayRateLimiter(
            min_delay_seconds=config.min_delay_seconds,
            jitter_seconds=config.jitter_seconds,
        )
    else:
        rate_limiter = config.rate_limiter

    # Cache:
    # - jeśli config.cache jest ustawione -> użyj
    # - jeśli nie -> default WikipediaCachePolicy (plikowy)
    if config.cache is None:
        cache: ResponseCache | None = WikipediaCachePolicy.with_file_cache(
            cache_dir=config.cache_dir,
            ttl_days=config.cache_ttl_days,
        )
    else:
        cache = config.cache

    return retry_policy, rate_limiter, cache


class HttpClient(BaseHttpClient):
    """Klient HTTP (requests) ze współdzieloną sesją, retry, rate-limit i cache."""

    def __init__(
        self,
        *,
        session: Optional[requests.Session] = None,
        config: HttpClientConfig | None = None,
        # legacy overrides (DEPRECATED):
        headers: Optional[Dict[str, str]] = None,
        timeout: int | None = None,
        retries: int | None = None,
        backoff_seconds: float | None = None,
        min_delay_seconds: float | None = None,
        jitter_seconds: float | None = None,
        retry_policy: RetryPolicy | None = None,
        rate_limiter: RateLimiter | None = None,
        cache: ResponseCache | None = None,
        cache_dir: Path | str | None = None,
        cache_ttl_days: int | None = None,
    ) -> None:
        session = session or requests.Session()

        config = _resolve_config(
            config,
            headers=headers,
            timeout=timeout,
            retries=retries,
            backoff_seconds=backoff_seconds,
            min_delay_seconds=min_delay_seconds,
            jitter_seconds=jitter_seconds,
            retry_policy=retry_policy,
            rate_limiter=rate_limiter,
            cache=cache,
            cache_dir=cache_dir,
            cache_ttl_days=cache_ttl_days,
        )

        eff_retry, eff_rate, eff_cache = _build_effective_policies(config)

        super().__init__(
            session=session,
            headers=config.headers,
            timeout=config.timeout,
            retry_policy=eff_retry,
            rate_limiter=eff_rate,
            cache=eff_cache,
            request_exception_cls=requests.RequestException,
        )

    def get(
        self,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> HttpResponseProtocol:
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
        config: HttpClientConfig | None = None,
        # legacy overrides (DEPRECATED):
        headers: Optional[Dict[str, str]] = None,
        timeout: int | None = None,
        retries: int | None = None,
        backoff_seconds: float | None = None,
        min_delay_seconds: float | None = None,
        jitter_seconds: float | None = None,
        retry_policy: RetryPolicy | None = None,
        rate_limiter: RateLimiter | None = None,
        cache: ResponseCache | None = None,
        cache_dir: Path | str | None = None,
        cache_ttl_days: int | None = None,
    ) -> None:
        session = session or requests_shim.Session()

        config = _resolve_config(
            config,
            headers=headers,
            timeout=timeout,
            retries=retries,
            backoff_seconds=backoff_seconds,
            min_delay_seconds=min_delay_seconds,
            jitter_seconds=jitter_seconds,
            retry_policy=retry_policy,
            rate_limiter=rate_limiter,
            cache=cache,
            cache_dir=cache_dir,
            cache_ttl_days=cache_ttl_days,
        )

        eff_retry, eff_rate, eff_cache = _build_effective_policies(config)

        super().__init__(
            session=session,
            headers=config.headers,
            timeout=config.timeout,
            retry_policy=eff_retry,
            rate_limiter=eff_rate,
            cache=eff_cache,
            request_exception_cls=requests_shim.RequestException,
        )

    def get(
        self,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> HttpResponseProtocol:
        return self._request_with_retries(
            url,
            headers=headers,
            timeout=timeout,
            request_func=self.session.get,
        )
