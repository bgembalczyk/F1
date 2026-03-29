from abc import ABC
from abc import abstractmethod
from collections.abc import Mapping

from infrastructure.http_client.policies.cache_key_strategy import CacheKeyStrategy
from infrastructure.http_client.policies.cache_key_strategy import UrlOnlyCacheKeyStrategy

class ResponseCache(ABC):
    """Interfejs cache dla odpowiedzi."""

    @abstractmethod
    def get(self, cache_key: str) -> str | None:
        """Zwraca tekst z cache lub None."""

    @abstractmethod
    def set(self, cache_key: str, text: str) -> None:
        """Zapisuje tekst do cache."""

    def build_cache_key(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
    ) -> str | None:
        """Buduje cache_key; None oznacza pominięcie cache dla żądania."""
        return self.cache_key_strategy.build_key(url, headers=headers)

    @property
    def cache_key_strategy(self) -> CacheKeyStrategy:
        """Strategia budowania klucza cache (domyślnie URL-only)."""
        return UrlOnlyCacheKeyStrategy()
