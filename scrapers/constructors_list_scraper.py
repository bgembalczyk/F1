"""Canonical module for constructors list scraping."""

from scrapers.constructors_list import ConstructorsListScraper as LegacyConstructorsListScraper


class ConstructorsListScraper(LegacyConstructorsListScraper):
    """Canonical class alias aligned with module naming standard."""


__all__ = ["ConstructorsListScraper", "LegacyConstructorsListScraper"]
