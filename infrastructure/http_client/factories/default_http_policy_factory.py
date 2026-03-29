"""Fabryka domyślnych polityk HTTP."""

from infrastructure.http_client.caching.wiki import WikipediaCachePolicy
from infrastructure.http_client.config import HttpClientConfig
from infrastructure.http_client.policies.default_retry import DefaultRetryPolicy
from infrastructure.http_client.policies.min_delay_rate_limiter import (
    MinDelayRateLimiter,
)
from infrastructure.http_client.policies.rate_limiter import RateLimiter
from infrastructure.http_client.policies.response_cache import ResponseCache
from infrastructure.http_client.policies.retry import RetryPolicy


class DefaultHttpPolicyFactory:
    """Buduje retry/rate-limit/cache policy na bazie konfiguracji klienta."""

    @staticmethod
    def build_retry_policy(config: HttpClientConfig) -> RetryPolicy:
        if config.retry_policy is not None:
            return config.retry_policy
        return DefaultRetryPolicy(
            retries=config.retries,
            backoff_seconds=config.backoff_seconds,
        )

    @staticmethod
    def build_rate_limiter(config: HttpClientConfig) -> RateLimiter:
        if config.rate_limiter is not None:
            return config.rate_limiter
        return MinDelayRateLimiter(
            min_delay_seconds=config.min_delay_seconds,
            jitter_seconds=config.jitter_seconds,
        )

    @staticmethod
    def build_response_cache(config: HttpClientConfig) -> ResponseCache | None:
        if config.cache is not None:
            return config.cache
        return WikipediaCachePolicy.with_file_cache(
            cache_dir=config.cache_dir,
            ttl_days=config.cache_ttl_days,
        )
