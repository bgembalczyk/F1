"""Canonical module for circuits detail scraping."""

from scrapers.circuits_single_scraper import F1SingleCircuitScraper


class CircuitsDetailScraper(F1SingleCircuitScraper):
    """Canonical class alias aligned with module naming standard."""


__all__ = ["CircuitsDetailScraper", "F1SingleCircuitScraper"]
