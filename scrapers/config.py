from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from scrapers.base.options import HttpPolicy, default_http_policy

if TYPE_CHECKING:
    from scrapers.base.export.exporters import DataExporter
    from scrapers.base.html_fetcher import HtmlFetcher
    from scrapers.base.parsers import SoupParser


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
