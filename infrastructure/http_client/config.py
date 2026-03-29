"""Konfiguracja klienta HTTP."""

from dataclasses import dataclass
from pathlib import Path

from config.app_config_provider import AppConfigProvider
from infrastructure.http_client.policies.constants import DEFAULT_HTTP_BACKOFF_SECONDS
from infrastructure.http_client.policies.constants import DEFAULT_HTTP_RETRIES
from infrastructure.http_client.policies.constants import DEFAULT_HTTP_TIMEOUT
from infrastructure.http_client.policies.rate_limiter import RateLimiter
from infrastructure.http_client.policies.response_cache import ResponseCache
from infrastructure.http_client.policies.retry import RetryPolicy


@dataclass
class HttpClientConfig:
    """Zbiór ustawień współdzielonych przez klientów HTTP."""

    timeout: int = DEFAULT_HTTP_TIMEOUT
    retries: int = DEFAULT_HTTP_RETRIES
    backoff_seconds: float = DEFAULT_HTTP_BACKOFF_SECONDS
    min_delay_seconds: float = 1.5
    jitter_seconds: float = 0.7
    retry_policy: RetryPolicy | None = None
    rate_limiter: RateLimiter | None = None
    cache: ResponseCache | None = None
    cache_dir: Path | str | None = None
    cache_ttl_days: int = 30
    headers: dict[str, str] | None = None


def default_http_client_config(
    provider: AppConfigProvider | None = None,
) -> HttpClientConfig:
    """Buduje domyślną konfigurację HTTP przez AppConfigProvider."""
    resolved_provider = provider or AppConfigProvider()
    http_config = resolved_provider.get_http_config()
    return HttpClientConfig(timeout=http_config.timeout_seconds)
