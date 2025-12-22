"""Interfejsy dla strategii retry, rate limiting i cachowania."""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Optional


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


class RateLimiter(ABC):
    """Interfejs strategii limitowania tempa."""

    @abstractmethod
    def wait(self, url: str) -> None:
        """Wymusza opóźnienie przed wykonaniem requestu."""


class ResponseCache(ABC):
    """Interfejs cache dla odpowiedzi."""

    @abstractmethod
    def get(self, url: str) -> Optional[str]:
        """Zwraca tekst z cache lub None."""

    @abstractmethod
    def set(self, url: str, text: str) -> None:
        """Zapisuje tekst do cache."""
