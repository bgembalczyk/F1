import pytest

from scrapers.adapters.cache_adapter import CacheAdapter
from tests.scrapers.base.dummy_classes import MemoryCache2
from tests.scrapers.base.dummy_classes import ReadErrorCache
from tests.scrapers.base.dummy_classes import StubSourceAdapter
from tests.scrapers.base.dummy_classes import WriteErrorCache


def test_cache_adapter_cache_miss_fetches_from_source_and_populates_cache() -> None:
    source = StubSourceAdapter()
    cache = MemoryCache2()
    adapter = CacheAdapter(source_adapter=source, cache_adapter=cache)

    result = adapter.get("https://example.com/a")

    assert result == "fresh:https://example.com/a:1"
    assert source.calls == 1
    assert cache.store["https://example.com/a"] == result


def test_cache_adapter_cache_hit_uses_cached_value_without_hitting_source() -> None:
    source = StubSourceAdapter()
    cache = MemoryCache2()
    cache.store["https://example.com/a"] = "cached-value"
    adapter = CacheAdapter(source_adapter=source, cache_adapter=cache)

    result = adapter.get("https://example.com/a")

    assert result == "cached-value"
    assert source.calls == 0


def test_cache_adapter_refreshes_value_after_cache_eviction() -> None:
    source = StubSourceAdapter()
    cache = MemoryCache2()
    adapter = CacheAdapter(source_adapter=source, cache_adapter=cache)

    first = adapter.get("https://example.com/a")
    cache.store.pop("https://example.com/a")
    second = adapter.get("https://example.com/a")

    assert first != second
    assert source.calls == 2  # noqa: PLR2004


def test_cache_adapter_propagates_cache_read_error() -> None:
    source = StubSourceAdapter()
    adapter = CacheAdapter(source_adapter=source, cache_adapter=ReadErrorCache())

    with pytest.raises(OSError, match="cache read failed"):
        adapter.get("https://example.com/a")


def test_cache_adapter_propagates_cache_write_error() -> None:
    source = StubSourceAdapter()
    adapter = CacheAdapter(source_adapter=source, cache_adapter=WriteErrorCache())

    with pytest.raises(OSError, match="cache write failed"):
        adapter.get("https://example.com/a")


def test_cache_adapter_metadata_includes_cache_backend() -> None:
    source = StubSourceAdapter()
    cache = MemoryCache2()
    adapter = CacheAdapter(source_adapter=source, cache_adapter=cache)

    metadata = adapter.metadata

    assert metadata["source"] == "stub"
    assert metadata["cache"] is cache
