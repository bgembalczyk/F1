"""Canonical factory module for circuits domain."""

from scrapers.circuits_composition import CircuitScraperCompositionFactory


class CircuitsFactory(CircuitScraperCompositionFactory):
    """Canonical alias for circuit composition factory."""


__all__ = ["CircuitsFactory", "CircuitScraperCompositionFactory"]
