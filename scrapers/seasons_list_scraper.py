"""Deprecated compatibility module for seasons list scraper."""

from warnings import warn

from scrapers.seasons.list_scraper import SeasonsListScraper

warn(
    "scrapers.seasons_list_scraper is deprecated; use scrapers.seasons.list_scraper",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["SeasonsListScraper"]
