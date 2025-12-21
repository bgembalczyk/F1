"""Konfiguracja klienta HTTP."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from http_client.policies import RateLimiter, ResponseCache, RetryPolicy


@dataclass
class HttpClientConfig:
    """Zbiór ustawień współdzielonych przez klientów HTTP."""

    timeout: int = 10
    retries: int = 0
    backoff_seconds: float = 0.5
    min_delay_seconds: float = 1.5
    jitter_seconds: float = 0.7
    retry_policy: RetryPolicy | None = None
    rate_limiter: RateLimiter | None = None
    cache: ResponseCache | None = None
    cache_dir: Path | str | None = None
    cache_ttl_days: int = 30
    headers: Optional[Dict[str, str]] = None
