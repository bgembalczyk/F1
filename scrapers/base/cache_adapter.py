from pathlib import Path
from typing import Any, Optional

from infrastructure.http_client.caching.file import FileCache
from scrapers.base.source_adapter import SourceAdapter


class CacheAdapter(SourceAdapter[str]):
    """Cache'ujący adapter źródła oparty o pliki."""

    def __init__(
        self,
        *,
        source_adapter: SourceAdapter[str],
        cache_dir: Path | str,
        ttl_seconds: int = 0,
    ) -> None:
        self._source_adapter = source_adapter
        self._cache = FileCache(cache_dir=cache_dir, ttl_seconds=ttl_seconds)

    def get(self, source: Optional[str] = None, **kwargs: Any) -> str:
        if source is None:
            raise ValueError("CacheAdapter wymaga źródła (np. URL).")
        cached = self._cache.get(source)
        if cached is not None:
            return cached
        text = self._source_adapter.get(source, **kwargs)
        self._cache.set(source, text)
        return text
