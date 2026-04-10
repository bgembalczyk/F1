"""Canonical factory module for drivers domain."""

from scrapers.composition_drivers import DriverScraperCompositionFactory


class DriversFactory(DriverScraperCompositionFactory):
    """Canonical alias for driver composition factory."""


__all__ = ["DriversFactory", "DriverScraperCompositionFactory"]
