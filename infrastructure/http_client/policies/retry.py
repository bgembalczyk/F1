from abc import ABC
from abc import abstractmethod
from typing import Any


class RetryPolicy(ABC):
    """Interfejs strategii retry."""

    @property
    @abstractmethod
    def max_retries(self) -> int:
        """Maksymalna liczba ponowień."""

    @abstractmethod
    def should_retry(
            self,
            *,
            response: Any | None,
            exception: Exception | None,
            attempt: int,
    ) -> bool:
        """Czy ponawiać próbę?"""

    @abstractmethod
    def backoff_seconds(self, attempt: int) -> float:
        """Ile sekund odczekać przed retry."""
