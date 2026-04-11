"""DEPRECATED ENTRYPOINT: use scrapers.drivers.entrypoint.run_list_scraper."""

import warnings

from scrapers.legacy_impl.list_scraper_drivers_impl import F1DriversListScraper
from scrapers.legacy_impl.list_scraper_drivers_impl import TABLE_SCHEMA
from scrapers.parsers.section.drivers_list import DriversListSectionParser
from scrapers.parsers.table.drivers_list import DriversListTableParser

warnings.warn(
    "list_scraper_drivers is deprecated; use scrapers.drivers_list_scraper.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "DriversListTableParser",
    "DriversListSectionParser",
    "TABLE_SCHEMA",
    "F1DriversListScraper",
]
