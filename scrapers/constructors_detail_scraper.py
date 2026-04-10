"""Deprecated compatibility module for constructors detail scraper."""

from warnings import warn

from scrapers.constructors.single_scraper import ConstructorsDetailScraper

warn(
    "scrapers.constructors_detail_scraper is deprecated; use scrapers.constructors.single_scraper",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["ConstructorsDetailScraper"]
