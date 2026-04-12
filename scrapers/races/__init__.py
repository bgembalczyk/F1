"""Re-exports for scrapers.races namespace."""
from scrapers.combined_red_flagged_races import RedFlaggedRacesScraper
from scrapers.parsers.table.red_flagged_races import NonChampionshipsRacesTableMapper
from scrapers.parsers.table.red_flagged_races import WorldChampionshipsRacesTableMapper
from scrapers.parsers.wiki.base_nested_section.sub_section.non_championships_races import NonChampionshipsRacesSubSectionParser
from scrapers.parsers.wiki.base_nested_section.nested_section.red_flagged_races import RedFlaggedRacesSectionParser

__all__ = [
    "NonChampionshipsRacesSubSectionParser",
    "NonChampionshipsRacesTableMapper",
    "RedFlaggedRacesScraper",
    "RedFlaggedRacesSectionParser",
    "WorldChampionshipsRacesTableMapper",
]

