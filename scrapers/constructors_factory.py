"""Canonical factory module for constructors domain."""

from scrapers.constructors_composition import ConstructorScraperCompositionFactory


class ConstructorsFactory(ConstructorScraperCompositionFactory):
    """Canonical alias for constructor composition factory."""


__all__ = ["ConstructorsFactory", "ConstructorScraperCompositionFactory"]
