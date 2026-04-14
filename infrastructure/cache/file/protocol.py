from pathlib import Path

from infrastructure.cache.file.ttl import FileTtlCache
from infrastructure.cache.file.ttl import HttpResponseFileCacheAdapter
from infrastructure.http.protocols.text_cache import TextCacheProtocol


class FileCache(TextCacheProtocol):
    """Cache oparty o pliki z TTL."""

    def __init__(self, *, cache_dir: Path | str, ttl_seconds: int = 0) -> None:
        self._cache = FileTtlCache[str](
            cache_dir=cache_dir,
            ttl_seconds=ttl_seconds,
            adapter=HttpResponseFileCacheAdapter(),
        )

    def get(self, url: str) -> str | None:
        return self._cache.get(url)

    def set(self, url: str, text: str) -> None:
        self._cache.set(url, text)
