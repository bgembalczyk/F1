"""Canonical module for seasons list scraping."""

from scrapers.list_scraper_seasons import SeasonsListScraper as LegacySeasonsListScraper


class SeasonsListScraper(LegacySeasonsListScraper):
    """Canonical class alias aligned with module naming standard."""


__all__ = ["SeasonsListScraper", "LegacySeasonsListScraper"]
