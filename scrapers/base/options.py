from dataclasses import dataclass
from typing import Optional, cast

from infrastructure.http_client.clients.urllib_http import UrllibHttpClient
from infrastructure.http_client.config import HttpClientConfig
from infrastructure.http_client.interfaces.http_client_protocol import (
    HttpClientProtocol,
)
from infrastructure.http_client.policies.http import HttpPolicy
from scrapers.base.export.exporters import DataExporter
from scrapers.base.helpers.http import default_http_policy
from scrapers.base.source_adapter import SourceAdapter
from scrapers.base.parsers import SoupParser
from scrapers.base.html_fetcher import HtmlFetcher


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

    def with_fetcher(self, *, policy: HttpPolicy | None = None) -> HtmlFetcher:
        from scrapers.base.html_fetcher import HtmlFetcher

        if policy is not None:
            self.policy = policy

        if self.fetcher is None:
            if isinstance(self.source_adapter, HtmlFetcher):
                self.fetcher = self.source_adapter
            else:
                resolved_policy = self.to_http_policy()
                http_client = self._ensure_http_client(resolved_policy)
                self.fetcher = HtmlFetcher(
                    policy=resolved_policy,
                    http_client=http_client,
                )
                if self.source_adapter is None:
                    self.source_adapter = self.fetcher
        return self.fetcher

    def with_source_adapter(
        self,
        *,
        policy: HttpPolicy | None = None,
    ) -> SourceAdapter:
        from scrapers.base.html_fetcher import HtmlFetcher

        if policy is not None:
            self.policy = policy

        if self.source_adapter is None:
            if self.fetcher is not None:
                self.source_adapter = self.fetcher
            else:
                resolved_policy = self.to_http_policy()
                http_client = self._ensure_http_client(resolved_policy)
                self.fetcher = HtmlFetcher(
                    policy=resolved_policy,
                    http_client=http_client,
                )
                self.source_adapter = self.fetcher
        elif isinstance(self.source_adapter, HtmlFetcher):
            self.fetcher = self.source_adapter
        return self.source_adapter
