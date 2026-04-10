"""Deprecated compatibility module for grands prix detail scraper."""

from warnings import warn

from scrapers.grands_prix.single_scraper import GrandsPrixDetailScraper

warn(
    "scrapers.grands_prix_detail_scraper is deprecated; use scrapers.grands_prix.single_scraper",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["GrandsPrixDetailScraper"]
