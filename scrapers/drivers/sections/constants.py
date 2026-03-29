from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from scrapers.base.table.columns.types import DriverListColumn
from scrapers.base.table.columns.types.constructor import ConstructorColumn
from scrapers.base.table.columns.types.engine import EngineColumn
from scrapers.base.table.columns.types.entrant import EntrantColumn
from scrapers.base.table.columns.types.position import PositionColumn
from scrapers.base.table.columns.types.tyre import TyreColumn
from scrapers.drivers.sections.common import DriverResultsSectionConfig

if TYPE_CHECKING:
    from collections.abc import Callable

from scrapers.base.table.columns.types import AutoColumn
from scrapers.base.table.columns.types import IntColumn
from scrapers.base.table.columns.types import LinksListColumn
from scrapers.base.table.columns.types import SkipColumn
from scrapers.base.table.columns.types import TextColumn
from scrapers.base.table.columns.types import UrlColumn
from scrapers.base.table.headers_shared import BASE_METRIC_HEADERS_TO_KEYS
from scrapers.base.table.headers_shared import POINTS_HEADER
from scrapers.base.table.headers_shared import POINTS_HEADER_TO_KEY
from scrapers.drivers.columns.points_or_text import PointsOrTextColumn
from scrapers.drivers.columns.series import SeriesColumn

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
    "Wins": BASE_METRIC_HEADERS_TO_KEYS["Wins"],
    "Poles": BASE_METRIC_HEADERS_TO_KEYS["Poles"],
    "F/Laps": "fastest_laps",
    "F/Lap": "fastest_laps",
    "Podiums": BASE_METRIC_HEADERS_TO_KEYS["Podiums"],
    POINTS_HEADER: POINTS_HEADER_TO_KEY[POINTS_HEADER],
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
