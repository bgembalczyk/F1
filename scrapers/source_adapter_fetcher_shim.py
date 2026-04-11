from __future__ import annotations

from infrastructure.http.policies.http import HttpPolicy
from infrastructure.http.protocols.text_cache import TextCacheProtocol
from scrapers.html_fetcher import HtmlFetcher
from scrapers.source_adapter import SourceAdapter


class SourceAdapterFetcherShim(HtmlFetcher):
    """Adapter exposing SourceAdapter as HtmlFetcher for legacy option wiring."""

    def __init__(self, source_adapter: SourceAdapter) -> None:
        self._source_adapter = source_adapter
        self.cache_adapter = None
        self.timeout = 10
        self.http_client = None
        self.policy = HttpPolicy(timeout=10, retries=0, cache=False)

    def set_cache(self, cache_adapter: TextCacheProtocol | None) -> None:
        self.cache_adapter = cache_adapter

    def get_text(self, url: str, *, timeout: int | None = None) -> str:
        _ = timeout
        return self._source_adapter.get(url)

    def get(self, url: str) -> str:
        return self._source_adapter.get(url)
