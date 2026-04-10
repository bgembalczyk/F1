"""Deprecated compatibility module for seasons detail scraper."""

from warnings import warn

from scrapers.seasons.single_scraper import SeasonsDetailScraper

warn(
    "scrapers.seasons_detail_scraper is deprecated; use scrapers.seasons.single_scraper",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["SeasonsDetailScraper"]
