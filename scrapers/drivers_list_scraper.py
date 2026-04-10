"""Canonical module for drivers list scraping."""

from scrapers.list_scraper_drivers import F1DriversListScraper


class DriversListScraper(F1DriversListScraper):
    """Canonical class alias aligned with module naming standard."""


__all__ = ["DriversListScraper", "F1DriversListScraper"]
