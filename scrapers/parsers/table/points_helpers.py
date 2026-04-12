"""Re-export of points table mappers for scrapers.parsers.table path compatibility."""
from scrapers.parsers.wiki.points_scoring_systems_history_table_mapper import (
    PointsScoringSystemsHistoryTableMapper,
)
from scrapers.parsers.wiki.shortened_races_points_table_mapper import (
    ShortenedRacesPointsTableMapper,
)
from scrapers.parsers.wiki.sprint_points_table_mapper import SprintPointsTableMapper

__all__ = [
    "PointsScoringSystemsHistoryTableMapper",
    "ShortenedRacesPointsTableMapper",
    "SprintPointsTableMapper",
]
