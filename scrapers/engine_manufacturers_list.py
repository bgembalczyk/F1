import warnings

from scrapers.legacy_impl.engine_manufacturers_list_impl import EngineManufacturersListScraper
from scrapers.legacy_impl.engine_manufacturers_list_impl import TABLE_SCHEMA
from scrapers.parsers.list.engine_manufacturers_list import IndianapolisOnlyListParser
from scrapers.parsers.section.engine_manufacturers_list import EngineManufacturersSectionParser
from scrapers.parsers.section.engine_manufacturers_list import IndianapolisOnlySubSectionParser
from scrapers.parsers.table.engine_manufacturers_list import EngineManufacturersTableParser

warnings.warn(
    "engine_manufacturers_list is deprecated; use canonical scraper entrypoints.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "EngineManufacturersTableParser",
    "IndianapolisOnlyListParser",
    "IndianapolisOnlySubSectionParser",
    "EngineManufacturersSectionParser",
    "TABLE_SCHEMA",
    "EngineManufacturersListScraper",
]
