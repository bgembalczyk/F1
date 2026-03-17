from __future__ import annotations

from collections.abc import Callable
from typing import Any

from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.constructor import ConstructorColumn
from scrapers.base.table.columns.types.driver_list import DriverListColumn
from scrapers.base.table.columns.types.engine import EngineColumn
from scrapers.base.table.columns.types.entrant import EntrantColumn
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.position import PositionColumn
from scrapers.base.table.columns.types.skip import SkipColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.columns.types.tyre import TyreColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.drivers.columns.points_or_text import PointsOrTextColumn
from scrapers.drivers.columns.series import SeriesColumn

CAREER_HIGHLIGHTS_REQUIRED_HEADERS = frozenset(
    {"Season", "Series", "Position", "Team", "Car"},
)
CAREER_SUMMARY_REQUIRED_HEADERS = frozenset({"Season", "Series", "Position"})
COMPLETE_RESULTS_REQUIRED_HEADER = "Year"

CAREER_HIGHLIGHTS_HEADER_TO_KEY = {
    "Season": "season",
    "Series": "series",
    "Position": "position",
    "Team": "team",
    "Car": "car",
}

CAREER_HIGHLIGHTS_COLUMN_FACTORY_BY_KEY: dict[str, Callable[[], Any]] = {
    "season": IntColumn,
    "series": UrlColumn,
    "position": PositionColumn,
    "team": EntrantColumn,
    "car": UrlColumn,
}

CAREER_SUMMARY_HEADER_TO_KEY = {
    "Season": "season",
    "Series": "series",
    "Position": "position",
    "Team": "team",
    "Races": "races",
    "Wins": "wins",
    "Poles": "poles",
    "F/Laps": "fastest_laps",
    "F/Lap": "fastest_laps",
    "Podiums": "podiums",
    "Points": "points",
}

CAREER_SUMMARY_COLUMN_FACTORY_BY_KEY: dict[str, Callable[[], Any]] = {
    "season": IntColumn,
    "series": SeriesColumn,
    "position": TextColumn,
    "team": EntrantColumn,
    "races": IntColumn,
    "wins": IntColumn,
    "poles": IntColumn,
    "fastest_laps": IntColumn,
    "podiums": IntColumn,
    "points": PointsOrTextColumn,
}

COMPLETE_RESULTS_HEADER_TO_KEY = {
    "Year": "year",
    "Team": "team",
    "Co-Drivers": "co_drivers",
    "Co-drivers": "co_drivers",
    "Car": "car",
    "Class": "class",
    "Laps": "laps",
    "Pos.": "pos",
    "Pos": "pos",
    "Class Pos.": "class_pos",
    "Class Pos": "class_pos",
    "Entrant": "entrant",
    "Chassis": "chassis",
    "Engine": "engine",
    "WDC": "wdc",
    "Points": "points",
    "Rank": "rank",
    "DC": "dc",
    "Qualifying": "qualifying",
    "Quali Race": "quali_race",
    "Main race": "main_race",
    "Tyres": "tyres",
    "No.": "no",
    "No": "no",
    "Start": "start",
    "Finish": "finish",
    "Stages won": "stages_won",
    "Pts": "points",
    "Pts.": "points",
    "Ref": "ref",
    "Make": "make",
    "Manufacturer": "manufacturer",
    "NGNC": "ngnc",
    "QH": "qh",
    "F": "f",
}

COMPLETE_RESULTS_COLUMN_FACTORY_BY_KEY: dict[str, Callable[[], Any]] = {
    "year": AutoColumn,
    "team": EntrantColumn,
    "co_drivers": DriverListColumn,
    "car": AutoColumn,
    "class": AutoColumn,
    "laps": IntColumn,
    "pos": PositionColumn,
    "class_pos": PositionColumn,
    "entrant": EntrantColumn,
    "chassis": lambda: LinksListColumn(text_for_missing_url=True),
    "engine": EngineColumn,
    "wdc": PositionColumn,
    "points": PointsOrTextColumn,
    "rank": PositionColumn,
    "dc": PositionColumn,
    "qualifying": PositionColumn,
    "quali_race": PositionColumn,
    "main_race": PositionColumn,
    "tyres": TyreColumn,
    "no": IntColumn,
    "start": PositionColumn,
    "finish": PositionColumn,
    "stages_won": IntColumn,
    "make": ConstructorColumn,
    "manufacturer": ConstructorColumn,
    "ngnc": PositionColumn,
    "qh": PositionColumn,
    "f": PositionColumn,
    "ref": SkipColumn,
}
