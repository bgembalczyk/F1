"""Deprecated compatibility module for drivers list scraper."""

from warnings import warn

from scrapers.drivers.list_scraper import DriversListScraper

warn(
    "scrapers.drivers_list_scraper is deprecated; use scrapers.drivers.list_scraper",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["DriversListScraper"]
