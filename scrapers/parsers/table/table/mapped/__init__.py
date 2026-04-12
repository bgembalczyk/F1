from .base import MappedWikiTableMapper
from .lap_records import LapRecordsWikiTableMapper
from .race_results import RaceResultsTableMapper
from .standings import StandingsTableMapper

__all__ = [
    "MappedWikiTableMapper",
    "StandingsTableMapper",
    "RaceResultsTableMapper",
    "LapRecordsWikiTableMapper",
]
