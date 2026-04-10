"""Canonical module for grands prix detail scraping."""

from scrapers.single_scraper_grands_prix import F1SingleGrandPrixScraper


class GrandsPrixDetailScraper(F1SingleGrandPrixScraper):
    """Canonical class alias aligned with module naming standard."""


__all__ = ["GrandsPrixDetailScraper", "F1SingleGrandPrixScraper"]
