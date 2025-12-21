from . import engine_manufacturers_list as F1_engine_manufacturers_list_scraper
from . import (
    indianapolis_only_engine_manufacturers_list as F1_indianapolis_only_engine_manufacturers_list_scraper,
)
from .engine_manufacturers_list import EngineManufacturersListScraper
from .indianapolis_only_engine_manufacturers_list import (
    IndianapolisOnlyEngineManufacturersListScraper,
)

F1EngineManufacturersListScraper = EngineManufacturersListScraper
F1IndianapolisOnlyEngineManufacturersListScraper = (
    IndianapolisOnlyEngineManufacturersListScraper
)

__all__ = [
    "EngineManufacturersListScraper",
    "IndianapolisOnlyEngineManufacturersListScraper",
    "F1EngineManufacturersListScraper",
    "F1IndianapolisOnlyEngineManufacturersListScraper",
    "F1_engine_manufacturers_list_scraper",
    "F1_indianapolis_only_engine_manufacturers_list_scraper",
]
