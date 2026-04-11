"""Compatibility package for legacy drivers scraper import paths."""

from scrapers.drivers_detail_scraper import DriversDetailScraper
from scrapers.drivers_list_scraper import DriversListScraper

__all__ = ["DriversListScraper", "DriversDetailScraper"]
