from abc import ABC
from abc import abstractmethod
from collections.abc import Mapping
from hashlib import sha256


class CacheKeyStrategy(ABC):
    """Strategia budowania klucza cache na podstawie żądania HTTP."""

    @abstractmethod
    def build_key(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
    ) -> str:
        """Buduje deterministyczny klucz cache."""


class UrlOnlyCacheKeyStrategy(CacheKeyStrategy):
    """Domyślna strategia kompatybilna wstecz: klucz oparty wyłącznie o URL."""

    def build_key(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
    ) -> str:
        return url


class SelectedHeadersCacheKeyStrategy(CacheKeyStrategy):
    """Strategia oparta o URL i wybrane nagłówki."""

    def __init__(self, *, header_names: list[str]) -> None:
        self._header_names = tuple(sorted(name.lower() for name in header_names))

    def build_key(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
    ) -> str:
        normalized_headers = {k.lower(): v for k, v in (headers or {}).items()}
        header_part = "|".join(
            f"{name}={normalized_headers.get(name, '')}" for name in self._header_names
        )
        raw_key = f"{url}||{header_part}"
        return sha256(raw_key.encode("utf-8")).hexdigest()
