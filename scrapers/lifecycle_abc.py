"""Backward-compatibility shim: ScraperLifecycleABC merged into WikiScraper."""

from scrapers.scraper_wiki import WikiScraper

ScraperLifecycleABC = WikiScraper

__all__ = ["ScraperLifecycleABC"]
