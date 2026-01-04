from infrastructure.http_client.interfaces.http_client_protocol import (
    HttpClientProtocol,
)
from scrapers.base.cache_adapter import CacheBackend
from scrapers.base.source_adapter import SourceAdapter
from scrapers.base.options import HttpPolicy


class HtmlFetcher(SourceAdapter):
    """Warstwa pobierania HTML z opcjonalnym cache."""

    def __init__(
        self,
        *,
        policy: HttpPolicy,
        http_client: HttpClientProtocol,
        cache_adapter: CacheBackend | None = None,
    ) -> None:
        self.policy = policy
        self.http_client = http_client
        self.cache_adapter = cache_adapter
        self.timeout = policy.timeout
        self._metadata = {
            "policy": policy,
            "cache": cache_adapter,
            "retries": policy.retries,
            "timeout": policy.timeout,
        }

    @property
    def metadata(self) -> dict[str, object]:
        return dict(self._metadata)

    def set_cache(self, cache_adapter: CacheBackend | None) -> None:
        self.cache_adapter = cache_adapter
        self._metadata["cache"] = cache_adapter

    def get_text(self, url: str, *, timeout: int | None = None) -> str:
        if self.cache_adapter is not None:
            cached = self.cache_adapter.get(url)
            if cached is not None:
                return cached
        text = self.http_client.get_text(url, timeout=timeout or self.timeout)
        if self.cache_adapter is not None:
            self.cache_adapter.set(url, text)
        return text

    def get(self, url: str) -> str:
        return self.get_text(url)
