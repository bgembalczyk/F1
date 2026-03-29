import time
from hashlib import sha256
from pathlib import Path

from infrastructure.http_client.policies.cache_key_strategy import CacheKeyStrategy
from infrastructure.http_client.policies.cache_key_strategy import UrlOnlyCacheKeyStrategy
from infrastructure.http_client.policies.response_cache import ResponseCache


class FileCache(ResponseCache):
    """Cache oparty o pliki z TTL."""

    def __init__(
        self,
        *,
        cache_dir: Path | str,
        ttl_seconds: int = 0,
        cache_key_strategy: CacheKeyStrategy | None = None,
    ) -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = max(0, int(ttl_seconds))
        self._cache_key_strategy = cache_key_strategy or UrlOnlyCacheKeyStrategy()

    @property
    def cache_key_strategy(self) -> CacheKeyStrategy:
        return self._cache_key_strategy

    def get(self, cache_key: str) -> str | None:
        path = self._cache_path_for_key(cache_key)
        if not self._is_cache_fresh(path):
            return None
        return path.read_text(encoding="utf-8")

    def set(self, cache_key: str, text: str) -> None:
        path = self._cache_path_for_key(cache_key)
        path.write_text(text, encoding="utf-8")

    def _cache_path_for_key(self, cache_key: str) -> Path:
        digest = sha256(cache_key.encode("utf-8")).hexdigest()
        return self.cache_dir / f"{digest}.html"

    def _is_cache_fresh(self, path: Path) -> bool:
        # ttl_seconds == 0 => cache wyłączony
        if not path.exists() or self.ttl_seconds <= 0:
            return False
        age_seconds = time.time() - path.stat().st_mtime
        return age_seconds <= self.ttl_seconds
