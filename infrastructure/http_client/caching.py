"""Implementacje cachowania odpowiedzi HTTP."""

import time
from hashlib import sha256
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from infrastructure.http_client.policies import ResponseCache


class FileCache(ResponseCache):
    """Cache oparty o pliki z TTL."""

    def __init__(self, *, cache_dir: Path | str, ttl_seconds: int = 0) -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = max(0, int(ttl_seconds))

    def get(self, url: str) -> Optional[str]:
        path = self._cache_path_for_url(url)
        if not self._is_cache_fresh(path):
            return None
        return path.read_text(encoding="utf-8")

    def set(self, url: str, text: str) -> None:
        path = self._cache_path_for_url(url)
        path.write_text(text, encoding="utf-8")

    def _cache_path_for_url(self, url: str) -> Path:
        digest = sha256(url.encode("utf-8")).hexdigest()
        return self.cache_dir / f"{digest}.html"

    def _is_cache_fresh(self, path: Path) -> bool:
        # ttl_seconds == 0 => cache wyłączony
        if not path.exists() or self.ttl_seconds <= 0:
            return False
        age_seconds = time.time() - path.stat().st_mtime
        return age_seconds <= self.ttl_seconds


class WikipediaCachePolicy(ResponseCache):
    """Cache tylko dla Wikipedia."""

    def __init__(self, cache: ResponseCache) -> None:
        self.cache = cache

    def get(self, url: str) -> Optional[str]:
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
            cache_dir = Path(__file__).resolve().parents[2] / "data" / "wiki_cache"
        ttl_seconds = max(0, int(ttl_days)) * 24 * 60 * 60
        return cls(FileCache(cache_dir=cache_dir, ttl_seconds=ttl_seconds))

    @staticmethod
    def _is_wikipedia_url(url: str) -> bool:
        parsed = urlparse(url)
        hostname = (parsed.hostname or "").lower()
        return hostname == "wikipedia.org" or hostname.endswith(".wikipedia.org")
