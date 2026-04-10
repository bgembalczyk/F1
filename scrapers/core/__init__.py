"""Core scraper contract: abstractions and shared base components."""

from scrapers.core.composite_scraper import CompositeDataExtractor
from scrapers.core.errors import DomainParseError
from scrapers.core.errors import ScraperNetworkError
from scrapers.core.errors import ScraperParseError
from scrapers.core.options import ScraperOptions
from scrapers.core.run_config import RunConfig
from scrapers.core.runner import ScraperRunner

__all__ = [
    "CompositeDataExtractor",
    "DomainParseError",
    "RunConfig",
    "ScraperNetworkError",
    "ScraperOptions",
    "ScraperParseError",
    "ScraperRunner",
]
