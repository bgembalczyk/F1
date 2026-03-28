from collections import deque

from infrastructure.gemini.constants import RPD_WINDOW
from infrastructure.gemini.constants import RPM_WINDOW
from infrastructure.gemini.model_config import ModelConfig


class ModelState:
    """Wewnętrzny stan rate-limitera dla jednego modelu (sliding window)."""

    def __init__(self, config: ModelConfig) -> None:
        self.config = config
        self._rpm_timestamps: deque[float] = deque()
        self._rpd_timestamps: deque[float] = deque()

    @property
    def model(self) -> str:
        return self.config.model

    def is_available(self, now: float) -> bool:
        """Sprawdza, czy model nie przekroczył żadnego z limitów."""
        self._purge_rpm(now)
        self._purge_rpd(now)
        return (
            len(self._rpm_timestamps) < self.config.requests_per_minute
            and len(self._rpd_timestamps) < self.config.requests_per_day
        )

    def record_request(self, now: float) -> None:
        """Rejestruje znacznik czasu nowego zapytania."""
        self._rpm_timestamps.append(now)
        self._rpd_timestamps.append(now)

    def _purge_rpm(self, now: float) -> None:
        while (
            self._rpm_timestamps and now - self._rpm_timestamps[0] >= RPM_WINDOW
        ):
            self._rpm_timestamps.popleft()

    def _purge_rpd(self, now: float) -> None:
        while (
            self._rpd_timestamps and now - self._rpd_timestamps[0] >= RPD_WINDOW
        ):
            self._rpd_timestamps.popleft()
