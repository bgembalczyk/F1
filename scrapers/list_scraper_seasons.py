"""DEPRECATED ENTRYPOINT: use scrapers.seasons.entrypoint.run_list_scraper."""

import warnings

from scrapers.legacy_impl.list_scraper_seasons_impl import TABLE_SCHEMA
from scrapers.legacy_impl.list_scraper_seasons_impl import SeasonsListScraper
from scrapers.parsers.section.seasons_list import SeasonsSectionParser
from scrapers.parsers.table.seasons_list import SeasonsTableParser

warnings.warn(
    "list_scraper_seasons is deprecated; use scrapers.seasons_list_scraper.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "SeasonsTableParser",
    "SeasonsSectionParser",
    "TABLE_SCHEMA",
    "SeasonsListScraper",
]
