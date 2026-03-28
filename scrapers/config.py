from dataclasses import dataclass
from dataclasses import field

from scrapers.base.export.exporters import DataExporter
from scrapers.base.html_fetcher import HtmlFetcher
from scrapers.base.options import HttpPolicy
from scrapers.base.options import default_http_policy
from scrapers.base.parsers.soup import SoupParser


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
