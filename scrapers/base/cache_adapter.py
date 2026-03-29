from pathlib import Path
from typing import Any
from typing import Protocol

from infrastructure.http_client.caching.file import FileCache
from scrapers.base.source_adapter import SourceAdapter


class CacheBackend(Protocol):
    """Interfejs cache dla HTML (get/set)."""

    def get(self, key: str) -> str | None:
        """Zwraca tekst z cache lub None."""

    def set(self, key: str, text: str) -> None:
        """Zapisuje tekst do cache."""


class FileCacheBackend(CacheBackend):
    """Cache oparty o pliki z TTL."""

    def __init__(self, *, cache_dir: Path | str, ttl_seconds: int = 0) -> None:
        self._cache = FileCache(cache_dir=cache_dir, ttl_seconds=ttl_seconds)

    def get(self, key: str) -> str | None:
        return self._cache.get(key)

    def set(self, key: str, text: str) -> None:
        self._cache.set(key, text)


class CacheAdapter(SourceAdapter):
    """Cache'ujący adapter źródła oparty o interfejs cache."""

    def __init__(
        self,
        *,
        source_adapter: SourceAdapter,
        cache_adapter: CacheBackend,
    ) -> None:
        self._source_adapter = source_adapter
        self._cache = cache_adapter

    @property
    def metadata(self) -> dict[str, object]:
        metadata = dict(getattr(self._source_adapter, "metadata", {}))
        metadata["cache"] = self._cache
        return metadata

    def get(self, url: str, **kwargs: Any) -> str:
        cached = self._cache.get(url)
        if cached is not None:
            return cached
        text = self._source_adapter.get(url, **kwargs)
        self._cache.set(url, text)
        return text
