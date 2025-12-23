from __future__ import annotations

from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn

BASE_STATS_MAP = {
    "Seasons": "seasons",
    "Races Entered": "races_entered",
    "Races Started": "races_started",
    "Wins": "wins",
    "Points": "points",
    "Poles": "poles",
    "FL": "fastest_laps",
    "Podiums": "podiums",
    "WCC": "wcc",
    "WDC": "wdc",
}

BASE_STATS_COLUMNS = {
    "seasons": SeasonsColumn(),
    "races_entered": IntColumn(),
    "races_started": IntColumn(),
    "wins": IntColumn(),
    "points": IntColumn(),
    "poles": IntColumn(),
    "fastest_laps": IntColumn(),
    "podiums": IntColumn(),
    "wcc": IntColumn(),
    "wdc": IntColumn(),
}
