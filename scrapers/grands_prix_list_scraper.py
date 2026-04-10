"""Deprecated compatibility module for grands prix list scraper."""

from warnings import warn

from scrapers.grands_prix.list_scraper import GrandsPrixListScraper

warn(
    "scrapers.grands_prix_list_scraper is deprecated; use scrapers.grands_prix.list_scraper",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["GrandsPrixListScraper"]
