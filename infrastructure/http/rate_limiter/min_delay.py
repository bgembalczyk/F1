"""Implementacje rate limiting."""

import asyncio
import random
import time
from collections.abc import Callable

from infrastructure.http.rate_limiter.base import RateLimiter


class MinDelayRateLimiter(RateLimiter):
    """Minimalny odstęp + jitter między requestami."""

    def __init__(
        self,
        *,
        min_delay_seconds: float = 1.5,
        jitter_seconds: float = 0.7,
        should_limit: Callable[[str], bool] | None = None,
    ) -> None:
        self.min_delay_seconds = max(0.0, float(min_delay_seconds))
        self.jitter_seconds = max(0.0, float(jitter_seconds))
        self.should_limit = should_limit
        self._last_request_ts: float = 0.0

    def wait(self, url: str) -> None:
        if self.should_limit is not None and not self.should_limit(url):
            return
        now = time.monotonic()
        elapsed = now - self._last_request_ts
        delay = self.min_delay_seconds - elapsed
        if delay > 0:
            jitter = random.random() * self.jitter_seconds
            self._last_request_ts = now + delay + jitter
            time.sleep(delay + jitter)
        else:
            self._last_request_ts = now

    async def wait_async(self, url: str) -> None:
        if self.should_limit is not None and not self.should_limit(url):
            return
        now = time.monotonic()
        elapsed = now - self._last_request_ts
        delay = self.min_delay_seconds - elapsed
        if delay > 0:
            jitter = random.random() * self.jitter_seconds
            self._last_request_ts = now + delay + jitter
            await asyncio.sleep(delay + jitter)
        else:
            self._last_request_ts = now


__all__ = [
    "MinDelayRateLimiter",
]
