from infrastructure.http_client.policies.response_cache import TextCacheProtocol
from scrapers.base.source_adapter import SourceAdapter

# Alias zachowujący dotychczasowe nazewnictwo po stronie scraperów.
CacheBackend = TextCacheProtocol


class CacheAdapter(SourceAdapter):
    """Cache'ujący adapter źródła oparty o interfejs cache."""

    def __init__(
        self,
        *,
        source_adapter: SourceAdapter,
        cache_adapter: TextCacheProtocol,
    ) -> None:
        self._source_adapter = source_adapter
        self._cache = cache_adapter

    @property
    def metadata(self) -> dict[str, object]:
        metadata = dict(getattr(self._source_adapter, "metadata", {}))
        metadata["cache"] = self._cache
        return metadata

    def get(self, url: str) -> str:
        cached = self._cache.get(url)
        if cached is not None:
            return cached
        text = self._source_adapter.get(url)
        self._cache.set(url, text)
        return text
