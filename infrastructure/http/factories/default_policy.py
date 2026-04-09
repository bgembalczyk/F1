"""Fabryka domyślnych polityk HTTP."""
from cache.wiki_policy import WikipediaCachePolicy
from http.config import HttpClientConfig
from http.policies.default_retry import DefaultRetryPolicy
from http.policies.min_delay_rate_limiter import MinDelayRateLimiter
from http.policies.rate_limiter import RateLimiter
from http.policies.response_cache import TextCacheProtocol
from http.policies.retry import RetryPolicy


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
    def build_response_cache(config: HttpClientConfig) -> TextCacheProtocol | None:
        if config.cache is not None:
            return config.cache
        return WikipediaCachePolicy.with_file_cache(
            cache_dir=config.cache_dir,
            ttl_days=config.cache_ttl_days,
        )


__all__ = ["DefaultHttpPolicyFactory"]
