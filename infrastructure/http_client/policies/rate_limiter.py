from abc import ABC
from abc import abstractmethod


class RateLimiter(ABC):
    """Interfejs strategii limitowania tempa."""

    @abstractmethod
    def wait(self, url: str) -> None:
        """Wymusza opóźnienie przed wykonaniem requestu."""
