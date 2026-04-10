"""Canonical factory module for seasons domain."""

from scrapers.composition_seasons import SeasonScraperCompositionFactory


class SeasonsFactory(SeasonScraperCompositionFactory):
    """Canonical alias for season composition factory."""


__all__ = ["SeasonsFactory", "SeasonScraperCompositionFactory"]
