"""Konfiguracja klienta HTTP."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from infrastructure.http_client.policies.defaults import (
    DEFAULT_HTTP_BACKOFF_SECONDS,
    DEFAULT_HTTP_RETRIES,
    DEFAULT_HTTP_TIMEOUT,
)
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
    headers: Optional[Dict[str, str]] = None
