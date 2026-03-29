from infrastructure.http_client.caching.file import FileCache
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

    def get_text(self, url: str, *, _timeout: int | None = None) -> str:
        self.calls.append(url)
        return f"html-{url}"


def test_file_cache_returns_cached_data(tmp_path):
    cache = FileCache(cache_dir=tmp_path, ttl_seconds=60)

    cache.set("key", "value")

    assert cache.get("key") == "value"
    assert cache.get("missing") is None
