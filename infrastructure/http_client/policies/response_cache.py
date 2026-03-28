from abc import ABC
from abc import abstractmethod


class ResponseCache(ABC):
    """Interfejs cache dla odpowiedzi."""

    @abstractmethod
    def get(self, url: str) -> str | None:
        """Zwraca tekst z cache lub None."""

    @abstractmethod
    def set(self, url: str, text: str) -> None:
        """Zapisuje tekst do cache."""
