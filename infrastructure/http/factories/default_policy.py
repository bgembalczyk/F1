"""Fabryka domyślnych polityk HTTP."""

from infrastructure.cache.wiki_policy import WikipediaCachePolicy
from infrastructure.http.config import HttpClientConfig
from infrastructure.http.policies.retry.default import DefaultRetryPolicy
from infrastructure.http.protocols.text_cache import TextCacheProtocol
from infrastructure.http.rate_limiter.min_delay import MinDelayRateLimiter


class DefaultHttpPolicyFactory:
    """Buduje retry/rate-limit/cache policy na bazie konfiguracji klienta."""

    @staticmethod
    def build_retry_policy(config: HttpClientConfig) -> DefaultRetryPolicy:
        if config.retry_policy is not None:
            return config.retry_policy
        return DefaultRetryPolicy(
            retries=config.retries,
            backoff_seconds=config.backoff_seconds,
        )

    @staticmethod
    def build_rate_limiter(config: HttpClientConfig) -> MinDelayRateLimiter:
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
