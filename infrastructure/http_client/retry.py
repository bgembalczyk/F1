"""Implementacje strategii retry."""

import random
from typing import Any

from infrastructure.http_client.policies import RetryPolicy


class DefaultRetryPolicy(RetryPolicy):
    """Domyślna strategia retry dla błędów 429/5xx (+częsty 403 od bot-policy)."""

    def __init__(self, *, retries: int = 0, backoff_seconds: float = 0.5) -> None:
        self._max_retries = max(0, int(retries))
        self._backoff_seconds = max(0.0, float(backoff_seconds))

    @property
    def max_retries(self) -> int:
        return self._max_retries

    def should_retry(
        self,
        *,
        response: Any | None,
        exception: Exception | None,
        attempt: int,
    ) -> bool:
        if exception is not None:
            return True
        if response is None:
            return False

        status = int(getattr(response, "status_code", 0) or 0)
        if status == 429 or 500 <= status <= 599:
            return True

        # Wikipedia czasem zwraca 403 z treścią o robot policy / rate limit.
        if status == 403:
            body_text = (getattr(response, "text", "") or "").lower()
            if (
                "too many requests" in body_text
                or "robot policy" in body_text
                or "please respect our robot policy" in body_text
            ):
                return True

        return False

    def backoff_seconds(self, attempt: int) -> float:
        # Exponential backoff + jitter
        base = self._backoff_seconds * (2**attempt)
        return base + random.random()
