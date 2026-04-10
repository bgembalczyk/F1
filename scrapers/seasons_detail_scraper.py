"""Canonical module for seasons detail scraping."""

from scrapers.single_scraper_seasons import SingleSeasonScraper


class SeasonsDetailScraper(SingleSeasonScraper):
    """Canonical class alias aligned with module naming standard."""


__all__ = ["SeasonsDetailScraper", "SingleSeasonScraper"]
