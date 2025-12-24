from abc import ABC
from abc import abstractmethod
from typing import Optional


class ResponseCache(ABC):
    """Interfejs cache dla odpowiedzi."""

    @abstractmethod
    def get(self, url: str) -> Optional[str]:
        """Zwraca tekst z cache lub None."""

    @abstractmethod
    def set(self, url: str, text: str) -> None:
        """Zapisuje tekst do cache."""
