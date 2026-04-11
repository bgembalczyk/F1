"""Re-export module for seasons list parser components."""

from scrapers.parsers.section.seasons_list import SeasonsSectionParser
from scrapers.parsers.table.seasons_list import SeasonsTableParser

__all__ = ["SeasonsSectionParser", "SeasonsTableParser"]
