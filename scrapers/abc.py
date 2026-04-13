"""Backward-compatibility shim: ABCScraper is now WikiScraper.

All scraper functionality has been merged into WikiScraper.
Import ABCScraper from here to keep existing code working.
"""

from scrapers.scraper_wiki import WikiScraper

#: Backward-compat alias — ABCScraper is WikiScraper.
ABCScraper = WikiScraper

__all__ = ["ABCScraper"]
