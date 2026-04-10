"""Canonical module for drivers detail scraping."""

from scrapers.single_scraper_drivers import SingleDriverScraper


class DriversDetailScraper(SingleDriverScraper):
    """Canonical class alias aligned with module naming standard."""


__all__ = ["DriversDetailScraper", "SingleDriverScraper"]
