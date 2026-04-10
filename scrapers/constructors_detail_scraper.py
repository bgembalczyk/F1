"""Canonical module for constructors detail scraping."""

from scrapers.constructors_single_scraper import SingleConstructorScraper


class ConstructorsDetailScraper(SingleConstructorScraper):
    """Canonical class alias aligned with module naming standard."""


__all__ = ["ConstructorsDetailScraper", "SingleConstructorScraper"]
