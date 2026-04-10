"""Canonical seasons scraper modules."""

from .list_scraper import SeasonsListScraper
from .single_scraper import SeasonsDetailScraper
from .complete_extractor import CompleteSeasonDataExtractor

__all__ = [
    "SeasonsListScraper",
    "SeasonsDetailScraper",
    "CompleteSeasonDataExtractor",
]
