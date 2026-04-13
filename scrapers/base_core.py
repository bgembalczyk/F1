"""Backward-compatibility shim: BaseScraperCore merged into WikiScraper."""

from scrapers.scraper_wiki import WikiScraper

BaseScraperCore = WikiScraper

__all__ = ["BaseScraperCore"]
