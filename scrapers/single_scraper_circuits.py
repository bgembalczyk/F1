"""Backward-compatibility shim. Use F1SingleCircuitScraper from circuits_single_scraper."""

from scrapers.circuits_single_scraper import F1SingleCircuitScraper

CircuitsDetailScraper = F1SingleCircuitScraper

__all__ = ["CircuitsDetailScraper"]
