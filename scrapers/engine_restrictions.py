import warnings

from scrapers.legacy_impl.engine_restrictions_impl import TABLE_SCHEMA
from scrapers.legacy_impl.engine_restrictions_impl import EngineRestrictionsScraper
from scrapers.parsers.section.engine_restrictions import CurrentRulesSectionParser
from scrapers.parsers.section.engine_restrictions import EngineSubSectionParser
from scrapers.parsers.table.engine_restrictions import EngineRestrictionsTableParser

warnings.warn(
    "engine_restrictions is deprecated; use canonical scraper entrypoints.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "EngineRestrictionsTableParser",
    "EngineSubSectionParser",
    "CurrentRulesSectionParser",
    "TABLE_SCHEMA",
    "EngineRestrictionsScraper",
]
