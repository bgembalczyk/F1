from dataclasses import dataclass
from typing import Optional, cast

from infrastructure.http_client.caching.wiki import WikipediaCachePolicy
from infrastructure.http_client.clients.urllib_http import UrllibHttpClient
from infrastructure.http_client.config import HttpClientConfig
from infrastructure.http_client.interfaces.http_client_protocol import (
    HttpClientProtocol,
)
from infrastructure.http_client.policies.http import HttpPolicy
from infrastructure.http_client.policies.response_cache import ResponseCache
from scrapers.base.export.exporters import DataExporter
from scrapers.base.source_adapter import SourceAdapter
from scrapers.base.parsers import SoupParser
from scrapers.base.html_fetcher import HtmlFetcher


def default_http_policy() -> "HttpPolicy":
    return HttpPolicy(cache=WikipediaCachePolicy.with_file_cache())


def build_http_policy(
    *,
    timeout: int = 10,
    retries: int = 0,
    cache: ResponseCache | None = None,
) -> HttpPolicy:
    return HttpPolicy(
        timeout=timeout,
        retries=retries,
        cache=cache,
    )


def init_scraper_options(
    options: "ScraperOptions | None",
    *,
    include_urls: bool | None = None,
) -> "ScraperOptions":
    resolved = options or ScraperOptions()
    if include_urls is not None:
        resolved.include_urls = include_urls
    return resolved


@dataclass(slots=True)
class ScraperOptions:
    """
    Konfiguracja scrapera.
    """

    include_urls: bool = True
    exporter: Optional[DataExporter] = None
    fetcher: HtmlFetcher | None = None
    source_adapter: SourceAdapter | None = None
    parser: SoupParser | None = None
    policy: HttpPolicy | None = None
    http_client: Optional[HttpClientProtocol] = None

    def __post_init__(self) -> None:
        if self.policy is None:
            self.policy = default_http_policy()

    def to_http_policy(self) -> HttpPolicy:
        if self.policy is not None:
            return self.policy
        self.policy = default_http_policy()
        return self.policy

    def _ensure_http_client(self, policy: HttpPolicy) -> HttpClientProtocol:
        if self.http_client is None:
            client_config = HttpClientConfig(
                timeout=policy.timeout,
                retries=policy.retries,
                cache=policy.cache,
            )
            self.http_client = cast(
                HttpClientProtocol,
                UrllibHttpClient(
                    config=client_config,
                ),
            )
        return self.http_client

    def with_fetcher(self) -> HtmlFetcher:
        from scrapers.base.html_fetcher import HtmlFetcher

        if self.fetcher is None:
            if isinstance(self.source_adapter, HtmlFetcher):
                self.fetcher = self.source_adapter
            else:
                policy = self.to_http_policy()
                http_client = self._ensure_http_client(policy)
                self.fetcher = HtmlFetcher(policy=policy, http_client=http_client)
                if self.source_adapter is None:
                    self.source_adapter = self.fetcher
        return self.fetcher

    def with_source_adapter(self) -> SourceAdapter:
        from scrapers.base.html_fetcher import HtmlFetcher

        if self.source_adapter is None:
            if self.fetcher is not None:
                self.source_adapter = self.fetcher
            else:
                policy = self.to_http_policy()
                http_client = self._ensure_http_client(policy)
                self.fetcher = HtmlFetcher(policy=policy, http_client=http_client)
                self.source_adapter = self.fetcher
        elif isinstance(self.source_adapter, HtmlFetcher):
            self.fetcher = self.source_adapter
        return self.source_adapter
