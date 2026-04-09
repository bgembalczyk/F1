from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from scrapers.base.table.columns import types as col
from scrapers.base.table.headers_shared import BASE_METRIC_HEADERS_TO_KEYS
from scrapers.base.table.headers_shared import POINTS_HEADER
from scrapers.base.table.headers_shared import POINTS_HEADER_TO_KEY
from scrapers.drivers.drivers_columns.points_or_text import PointsOrTextColumn
from scrapers.drivers.drivers_columns.series import SeriesColumn
from scrapers.drivers.drivers_sections.common import DriverResultsSectionConfig

if TYPE_CHECKING:
    from collections.abc import Callable


COMPLETE_RESULTS_REQUIRED_HEADER = "Year"

UNKNOWN_VALUE = "unknown"


CAREER_HIGHLIGHTS_REQUIRED_HEADERS = frozenset(
    {"Season", "Series", "Position", "Team", "Car"},
)
CAREER_SUMMARY_REQUIRED_HEADERS = frozenset({"Season", "Series", "Position"})


CAREER_HIGHLIGHTS_HEADER_TO_KEY = {
    "Season": "season",
    "Series": "series",
    "Position": "position",
    "Team": "team",
    "Car": "car",
}

CAREER_HIGHLIGHTS_COLUMN_FACTORY_BY_KEY: dict[str, Callable[[], Any]] = {
    "season": col.IntColumn,
    "series": col.UrlColumn,
    "position": col.PositionColumn,
    "team": col.EntrantColumn,
    "car": col.UrlColumn,
}

CAREER_SUMMARY_HEADER_TO_KEY = {
    "Season": "season",
    "Series": "series",
    "Position": "position",
    "Team": "team",
    "Races": "races",
    "Wins": BASE_METRIC_HEADERS_TO_KEYS["Wins"],
    "Poles": BASE_METRIC_HEADERS_TO_KEYS["Poles"],
    "F/Laps": "fastest_laps",
    "F/Lap": "fastest_laps",
    "Podiums": BASE_METRIC_HEADERS_TO_KEYS["Podiums"],
    POINTS_HEADER: POINTS_HEADER_TO_KEY[POINTS_HEADER],
}

CAREER_SUMMARY_COLUMN_FACTORY_BY_KEY: dict[str, Callable[[], Any]] = {
    "season": col.IntColumn,
    "series": SeriesColumn,
    "position": col.TextColumn,
    "team": col.EntrantColumn,
    "races": col.IntColumn,
    "wins": col.IntColumn,
    "poles": col.IntColumn,
    "fastest_laps": col.IntColumn,
    "podiums": col.IntColumn,
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
    **POINTS_HEADER_TO_KEY,
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
    "Ref": "ref",
    "Make": "make",
    "Manufacturer": "manufacturer",
    "NGNC": "ngnc",
    "QH": "qh",
    "F": "f",
}

COMPLETE_RESULTS_COLUMN_FACTORY_BY_KEY: dict[str, Callable[[], Any]] = {
    "year": col.AutoColumn,
    "team": col.EntrantColumn,
    "co_drivers": col.DriverListColumn,
    "car": col.AutoColumn,
    "class": col.AutoColumn,
    "laps": col.IntColumn,
    "pos": col.PositionColumn,
    "class_pos": col.PositionColumn,
    "entrant": col.EntrantColumn,
    "chassis": lambda: col.LinksListColumn(text_for_missing_url=True),
    "engine": col.EngineColumn,
    "wdc": col.PositionColumn,
    "points": PointsOrTextColumn,
    "rank": col.PositionColumn,
    "dc": col.PositionColumn,
    "qualifying": col.PositionColumn,
    "quali_race": col.PositionColumn,
    "main_race": col.PositionColumn,
    "tyres": col.TyreColumn,
    "no": col.IntColumn,
    "start": col.PositionColumn,
    "finish": col.PositionColumn,
    "stages_won": col.IntColumn,
    "make": col.ConstructorColumn,
    "manufacturer": col.ConstructorColumn,
    "ngnc": col.PositionColumn,
    "qh": col.PositionColumn,
    "f": col.PositionColumn,
    "ref": col.SkipColumn,
}


CAREER_RESULTS_SECTION = DriverResultsSectionConfig(
    section_id="Career_results",
    section_label="Career",
    header_aliases=("Career results", "Career"),
)

RACING_RECORD_SECTION = DriverResultsSectionConfig(
    section_id="Racing_record",
    section_label="Racing record",
    header_aliases=("Racing record", "Racing career"),
)

NON_CHAMPIONSHIP_SECTION = DriverResultsSectionConfig(
    section_id="Non-championship",
    section_label="Non-championship",
    header_aliases=("Non-championship", "Non-championship races"),
)

SECTION_CONFIGS: tuple[tuple[DriverResultsSectionConfig, tuple[str, ...]], ...] = (
    (CAREER_RESULTS_SECTION, ("Karting_record",)),
    (RACING_RECORD_SECTION, ("Motorsport_career_results",)),
    (NON_CHAMPIONSHIP_SECTION, ("Non-championship_races",)),
)


__all__ = [
    "COMPLETE_RESULTS_REQUIRED_HEADER",
    "UNKNOWN_VALUE",
    "CAREER_HIGHLIGHTS_REQUIRED_HEADERS",
    "CAREER_SUMMARY_REQUIRED_HEADERS",
    "CAREER_HIGHLIGHTS_HEADER_TO_KEY",
    "CAREER_HIGHLIGHTS_COLUMN_FACTORY_BY_KEY",
    "CAREER_SUMMARY_HEADER_TO_KEY",
    "CAREER_SUMMARY_COLUMN_FACTORY_BY_KEY",
    "COMPLETE_RESULTS_HEADER_TO_KEY",
    "COMPLETE_RESULTS_COLUMN_FACTORY_BY_KEY",
    "CAREER_RESULTS_SECTION",
    "RACING_RECORD_SECTION",
    "NON_CHAMPIONSHIP_SECTION",
    "SECTION_CONFIGS",
]
