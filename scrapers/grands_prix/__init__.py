"""Canonical grands prix scraper modules."""

from .list_scraper import GrandsPrixListScraper
from .single_scraper import GrandsPrixDetailScraper
from .complete_extractor import F1CompleteGrandPrixDataExtractor

__all__ = [
    "GrandsPrixListScraper",
    "GrandsPrixDetailScraper",
    "F1CompleteGrandPrixDataExtractor",
]
