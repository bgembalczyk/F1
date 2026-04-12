# ruff: noqa: E501, PLR2004

from infrastructure.http.policies.http import HttpPolicy
from scrapers.html_fetcher import HtmlFetcher


class StubHttpClient:
    def __init__(self, response: str = "page content") -> None:
        self._response = response
        self.calls: list[tuple[str, int | None]] = []

    def get_text(self, url: str, *, timeout: int | None = None) -> str:
        self.calls.append((url, timeout))
        return self._response


class MemoryCache:
    def __init__(self) -> None:
        self.store: dict[str, str] = {}

    def get(self, key: str) -> str | None:
        return self.store.get(key)

    def set(self, key: str, value: str) -> None:
        self.store[key] = value


def make_policy() -> HttpPolicy:
    return HttpPolicy(retries=0, timeout=10)


def test_html_fetcher_metadata_returns_copy() -> None:
    # Line 32: return dict(self._metadata)
    policy = make_policy()
    fetcher = HtmlFetcher(policy=policy, http_client=StubHttpClient())
    meta = fetcher.metadata
    assert isinstance(meta, dict)
    assert meta["policy"] is policy
    assert meta["retries"] == 0


def test_html_fetcher_set_cache_updates_cache_and_metadata() -> None:
    policy = make_policy()
    fetcher = HtmlFetcher(policy=policy, http_client=StubHttpClient())
    cache = MemoryCache()
    fetcher.set_cache(cache)
    assert fetcher.cache_adapter is cache
    assert fetcher.metadata["cache"] is cache


def test_html_fetcher_get_text_cache_miss_fetches_and_stores() -> None:
    # Lines 39-46: cache miss path
    http = StubHttpClient("fresh content")
    cache = MemoryCache()
    fetcher = HtmlFetcher(policy=make_policy(), http_client=http, cache_adapter=cache)

    result = fetcher.get_text("https://example.com/page")

    assert result == "fresh content"
    assert len(http.calls) == 1
    assert cache.store["https://example.com/page"] == "fresh content"


def test_html_fetcher_get_text_cache_hit_skips_http() -> None:
    # Lines 39-42: cache hit path
    http = StubHttpClient("fresh content")
    cache = MemoryCache()
    cache.store["https://example.com/page"] = "cached content"
    fetcher = HtmlFetcher(policy=make_policy(), http_client=http, cache_adapter=cache)

    result = fetcher.get_text("https://example.com/page")

    assert result == "cached content"
    assert len(http.calls) == 0


def test_html_fetcher_get_text_no_cache_fetches_directly() -> None:
    http = StubHttpClient("direct content")
    fetcher = HtmlFetcher(policy=make_policy(), http_client=http)

    result = fetcher.get_text("https://example.com/x")

    assert result == "direct content"
    assert len(http.calls) == 1


def test_html_fetcher_get_delegates_to_get_text() -> None:
    # Line 49: get() -> get_text()
    http = StubHttpClient("page data")
    fetcher = HtmlFetcher(policy=make_policy(), http_client=http)

    result = fetcher.get("https://example.com/y")

    assert result == "page data"
    assert len(http.calls) == 1
