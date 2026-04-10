from dataclasses import dataclass

from scrapers.abc import ABCScraper
from scrapers.run_config import RunConfig


@dataclass(frozen=True)
class ScraperCreationContext:
    scraper_cls: type[ABCScraper]
    run_config: RunConfig
    run_id: str
    supports_urls: bool
