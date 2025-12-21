from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from infrastructure.http_client.caching import WikipediaCachePolicy
from infrastructure.http_client.policies import ResponseCache

if TYPE_CHECKING:
    from scrapers.base.export.exporters import DataExporter
    from scrapers.base.html_fetcher import HtmlFetcher
    from scrapers.base.parsers import SoupParser


@dataclass(frozen=True)
class HttpPolicy:
    cache: ResponseCache | None = None
    retries: int = 0
    timeout: int = 10

    def __post_init__(self) -> None:
        if self.timeout <= 0:
            raise ValueError("timeout must be greater than 0")
        if self.retries < 0:
            raise ValueError("retries must be >= 0")


def default_http_policy() -> HttpPolicy:
    return HttpPolicy(cache=WikipediaCachePolicy.with_file_cache())


@dataclass(frozen=True)
class ScraperConfig:
    include_urls: bool = True
    exporter: DataExporter | None = None
    fetcher: HtmlFetcher | None = None
    parser: SoupParser | None = None
    policy: HttpPolicy = field(default_factory=default_http_policy)


def default_scraper_config() -> ScraperConfig:
    return ScraperConfig()


def default_config() -> ScraperConfig:
    return default_scraper_config()
