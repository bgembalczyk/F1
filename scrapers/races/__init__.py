"""Re-exports for scrapers.races namespace."""
from scrapers.combined_red_flagged_races import RedFlaggedRacesScraper
from scrapers.parsers.table.red_flagged_races import NonChampionshipsRacesTableParser
from scrapers.parsers.table.red_flagged_races import WorldChampionshipsRacesTableParser
from scrapers.parsers.wiki.sections.red_flagged_races_section_parser import NonChampionshipsRacesSubSectionParser
from scrapers.parsers.wiki.sections.red_flagged_races_section_parser import RedFlaggedRacesSectionParser

__all__ = [
    "NonChampionshipsRacesSubSectionParser",
    "NonChampionshipsRacesTableParser",
    "RedFlaggedRacesScraper",
    "RedFlaggedRacesSectionParser",
    "WorldChampionshipsRacesTableParser",
]
