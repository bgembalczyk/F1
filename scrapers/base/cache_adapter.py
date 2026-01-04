from __future__ import annotations

from pathlib import Path
from time import time
from typing import Any, Optional, Protocol

from infrastructure.http_client.caching.file import FileCache
from scrapers.base.source_adapter import SourceAdapter


class CacheBackend(Protocol):
    """Interfejs cache dla HTML (get/set)."""

    def get(self, key: str) -> Optional[str]:
        """Zwraca tekst z cache lub None."""

    def set(self, key: str, text: str) -> None:
        """Zapisuje tekst do cache."""


class MemoryCache(CacheBackend):
    """Cache w pamięci z opcjonalnym TTL."""

    def __init__(self, *, ttl_seconds: int = 0) -> None:
        self._ttl_seconds = max(0, int(ttl_seconds))
        self._store: dict[str, tuple[str, float]] = {}

    def get(self, key: str) -> Optional[str]:
        entry = self._store.get(key)
        if entry is None:
            return None
        text, timestamp = entry
        if self._ttl_seconds <= 0:
            return None
        if (time() - timestamp) > self._ttl_seconds:
            self._store.pop(key, None)
            return None
        return text

    def set(self, key: str, text: str) -> None:
        self._store[key] = (text, time())


class FileCacheBackend(CacheBackend):
    """Cache oparty o pliki z TTL."""

    def __init__(self, *, cache_dir: Path | str, ttl_seconds: int = 0) -> None:
        self._cache = FileCache(cache_dir=cache_dir, ttl_seconds=ttl_seconds)

    def get(self, key: str) -> Optional[str]:
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
