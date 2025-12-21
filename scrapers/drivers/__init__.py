from . import drivers_list as F1_drivers_list_scraper
from .drivers_list import DriversListScraper

F1DriversListScraper = DriversListScraper

__all__ = [
    "DriversListScraper",
    "F1DriversListScraper",
    "F1_drivers_list_scraper",
]
