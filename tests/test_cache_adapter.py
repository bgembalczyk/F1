from scrapers.base.cache_adapter import CacheAdapter
from scrapers.base.cache_adapter import FileCacheBackend
from scrapers.base.cache_adapter import MemoryCache
from scrapers.base.html_fetcher import HtmlFetcher
from scrapers.base.options import HttpPolicy
from scrapers.base.source_adapter import SourceAdapter


class _StubAdapter(SourceAdapter):
    def __init__(self) -> None:
        self.calls: list[str] = []

    @property
    def metadata(self) -> dict[str, object]:
        return {}

    def get(self, url: str) -> str:
        self.calls.append(url)
        return f"payload-{url}"


class _StubHttpClient:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def get_text(self, url: str, *, timeout: int | None = None) -> str:
        self.calls.append(url)
        return f"html-{url}"


def test_memory_cache_returns_cached_data():
    cache = MemoryCache(ttl_seconds=60)

    cache.set("key", "value")

    assert cache.get("key") == "value"
    assert cache.get("missing") is None


def test_file_cache_returns_cached_data(tmp_path):
    cache = FileCacheBackend(cache_dir=tmp_path, ttl_seconds=60)

    cache.set("key", "value")

    assert cache.get("key") == "value"
    assert cache.get("missing") is None


def test_cache_adapter_returns_cached_html():
    cache = MemoryCache(ttl_seconds=60)
    adapter = _StubAdapter()
    cached_adapter = CacheAdapter(source_adapter=adapter, cache_adapter=cache)

    first = cached_adapter.get("https://example.com")
    second = cached_adapter.get("https://example.com")

    assert first == "payload-https://example.com"
    assert second == "payload-https://example.com"
    assert adapter.calls == ["https://example.com"]


def test_html_fetcher_uses_cache_adapter():
    cache = MemoryCache(ttl_seconds=60)
    http_client = _StubHttpClient()
    fetcher = HtmlFetcher(
        policy=HttpPolicy(timeout=1),
        http_client=http_client,
        cache_adapter=cache,
    )

    first = fetcher.get("https://example.com")
    second = fetcher.get("https://example.com")

    assert first == "html-https://example.com"
    assert second == "html-https://example.com"
    assert http_client.calls == ["https://example.com"]
