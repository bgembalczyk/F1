from abc import ABC
from abc import abstractmethod


class RateLimiter(ABC):
    """Interfejs strategii limitowania tempa."""

    @abstractmethod
    def wait(self, url: str) -> None:
        """Wymusza opóźnienie przed wykonaniem requestu."""

    @abstractmethod
    async def wait_async(self, url: str) -> None:
        """Asynchronicznie wymusza opóźnienie przed wykonaniem requestu."""


__all__ = [
    "RateLimiter",
]
