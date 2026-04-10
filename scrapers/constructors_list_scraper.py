"""Deprecated compatibility module for constructors list scraper."""

from warnings import warn

from scrapers.constructors.list_scraper import ConstructorsListScraper

warn(
    "scrapers.constructors_list_scraper is deprecated; use scrapers.constructors.list_scraper",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["ConstructorsListScraper"]
