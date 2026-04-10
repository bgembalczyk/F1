"""Deprecated compatibility module for drivers detail scraper."""

from warnings import warn

from scrapers.drivers.single_scraper import DriversDetailScraper

warn(
    "scrapers.drivers_detail_scraper is deprecated; use scrapers.drivers.single_scraper",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["DriversDetailScraper"]
