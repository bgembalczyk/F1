from scrapers.wiki.parsers.elements.wiki_table.base import WikiTableBaseParser
from scrapers.wiki.parsers.elements.wiki_table.lap_records import LapRecordsWikiTableParser
from scrapers.wiki.parsers.elements.wiki_table.race_results import RaceResultsTableParser
from scrapers.wiki.parsers.elements.wiki_table.standings import StandingsTableParser

__all__ = [
    'LapRecordsWikiTableParser',
    'RaceResultsTableParser',
    'StandingsTableParser',
    'WikiTableBaseParser',
]
