"""Re-exports for scrapers.races namespace."""
from scrapers.combined_red_flagged_races import RedFlaggedRacesScraper
from scrapers.parsers.table.red_flagged_races_wiki_table import NonChampionshipsRacesTableParser
from scrapers.parsers.table.red_flagged_races_wiki_table import WorldChampionshipsRacesTableParser
from scrapers.parsers.table.red_flagged_races import NonChampionshipsRacesTableMapper
from scrapers.parsers.table.red_flagged_races import WorldChampionshipsRacesTableMapper
from scrapers.parsers.wiki.red_flagged_races import NonChampionshipsRacesSubSectionParser
from scrapers.parsers.wiki.red_flagged_races import RedFlaggedRacesSectionParser

__all__ = [
    "NonChampionshipsRacesSubSectionParser",
    "NonChampionshipsRacesTableMapper",
    "RedFlaggedRacesScraper",
    "RedFlaggedRacesSectionParser",
    "WorldChampionshipsRacesTableMapper",
]
