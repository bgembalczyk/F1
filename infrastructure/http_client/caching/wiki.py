from pathlib import Path
from collections.abc import Mapping
from urllib.parse import urlparse

from infrastructure.http_client.caching.file import FileCache
from infrastructure.http_client.policies.cache_key_strategy import CacheKeyStrategy
from infrastructure.http_client.policies.response_cache import ResponseCache


class WikipediaCachePolicy(ResponseCache):
    """Cache tylko dla Wikipedia."""

    def __init__(self, cache: ResponseCache) -> None:
        self.cache = cache

    @property
    def cache_key_strategy(self) -> CacheKeyStrategy:
        return self.cache.cache_key_strategy

    def build_cache_key(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
    ) -> str | None:
        if not self._is_wikipedia_url(url):
            return None
        return self.cache.build_cache_key(url, headers=headers)

    def get(self, cache_key: str) -> str | None:
        return self.cache.get(cache_key)

    def set(self, cache_key: str, text: str) -> None:
        self.cache.set(cache_key, text)

    @classmethod
    def with_file_cache(
        cls,
        *,
        cache_dir: Path | str | None = None,
        ttl_days: int = 30,
    ) -> "WikipediaCachePolicy":
        if cache_dir is None:
            cache_dir = Path(__file__).resolve().parents[3] / "data" / "wiki_cache"
        ttl_seconds = max(0, int(ttl_days)) * 24 * 60 * 60
        return cls(FileCache(cache_dir=cache_dir, ttl_seconds=ttl_seconds))

    @staticmethod
    def _is_wikipedia_url(url: str) -> bool:
        parsed = urlparse(url)
        hostname = (parsed.hostname or "").lower()
        return hostname == "wikipedia.org" or hostname.endswith(".wikipedia.org")
