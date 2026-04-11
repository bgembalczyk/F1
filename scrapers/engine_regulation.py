import warnings

from scrapers.legacy_impl.engine_regulation_impl import TABLE_SCHEMA
from scrapers.legacy_impl.engine_regulation_impl import EngineRegulationScraper
from scrapers.parsers.section.engine_regulation import EngineRegulationSubSectionParser
from scrapers.parsers.section.engine_regulation import HistorySectionParser
from scrapers.parsers.table.engine_regulation import EngineRegulationTableParser

warnings.warn(
    "engine_regulation is deprecated; use canonical scraper entrypoints.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "EngineRegulationTableParser",
    "EngineRegulationSubSectionParser",
    "HistorySectionParser",
    "TABLE_SCHEMA",
    "EngineRegulationScraper",
]
