"""Canonical grands prix single scraper module."""

from scrapers.single_scraper_grands_prix import F1SingleGrandPrixScraper


class GrandsPrixDetailScraper(F1SingleGrandPrixScraper):
    """Canonical grands prix detail scraper."""


__all__ = ["GrandsPrixDetailScraper"]
