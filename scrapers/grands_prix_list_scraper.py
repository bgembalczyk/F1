"""Canonical module for grands prix list scraping."""

from scrapers.list_scraper_grands_prix import (
    GrandsPrixListScraper as LegacyGrandsPrixListScraper,
)


class GrandsPrixListScraper(LegacyGrandsPrixListScraper):
    """Canonical class alias aligned with module naming standard."""


__all__ = ["GrandsPrixListScraper", "LegacyGrandsPrixListScraper"]
