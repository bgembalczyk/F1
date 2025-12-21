from . import grands_prix_list as F1_grands_prix_list_scraper
from .grands_prix_list import GrandsPrixListScraper

F1GrandsPrixListScraper = GrandsPrixListScraper

__all__ = [
    "GrandsPrixListScraper",
    "F1GrandsPrixListScraper",
    "F1_grands_prix_list_scraper",
]
