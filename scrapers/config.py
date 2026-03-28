from dataclasses import dataclass
from dataclasses import field
import warnings

from scrapers.base.export.exporters import DataExporter
from scrapers.base.html_fetcher import HtmlFetcher
from scrapers.base.options import HttpPolicy
from scrapers.base.options import default_http_policy
from scrapers.base.parsers.soup import SoupParser

@dataclass(frozen=True)
class RuntimeScraperConfig:
    """Runtime-level dependency wiring for scraper execution.

    This config defines *how* scraping is performed (network policy, fetcher,
    parser, exporter and URL inclusion), independent from page/table extraction
    rules.
    """

    include_urls: bool = True
    exporter: DataExporter | None = None
    fetcher: HtmlFetcher | None = None
    parser: SoupParser | None = None
    policy: HttpPolicy = field(default_factory=default_http_policy)


@dataclass(frozen=True)
class ScraperConfig(RuntimeScraperConfig):
    """Deprecated alias for RuntimeScraperConfig."""

    def __post_init__(self) -> None:
        warnings.warn(
            "ScraperConfig is deprecated; use RuntimeScraperConfig instead.",
            DeprecationWarning,
            stacklevel=2,
        )


def default_scraper_config() -> RuntimeScraperConfig:
    return RuntimeScraperConfig()


def default_config() -> RuntimeScraperConfig:
    return default_scraper_config()
