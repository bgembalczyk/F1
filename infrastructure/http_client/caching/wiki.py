from pathlib import Path
from urllib.parse import urlparse

from infrastructure.http_client.caching.file import FileCache
from infrastructure.http_client.policies.response_cache import ResponseCache


class WikipediaCachePolicy(ResponseCache):
    """Cache tylko dla Wikipedia."""

    def __init__(self, cache: ResponseCache) -> None:
        self.cache = cache

    def get(self, url: str) -> str | None:
        if not self._is_wikipedia_url(url):
            return None
        return self.cache.get(url)

    def set(self, url: str, text: str) -> None:
        if not self._is_wikipedia_url(url):
            return
        self.cache.set(url, text)

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
