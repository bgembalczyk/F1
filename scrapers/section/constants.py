from typing import Any
from typing import Callable

from scrapers.columns.factory import IntColumn
from scrapers.columns.types.auto import AutoColumn
from scrapers.columns.types.constructor.constructor import ConstructorColumn
from scrapers.columns.types.driver_list import DriverListColumn
from scrapers.columns.types.engine import EngineColumn
from scrapers.columns.types.entrant import EntrantColumn
from scrapers.columns.types.links_list import LinksListColumn
from scrapers.columns.types.points_or_text import PointsOrTextColumn
from scrapers.columns.types.position import PositionColumn
from scrapers.columns.types.series import SeriesColumn
from scrapers.columns.types.skip import SkipColumn
from scrapers.columns.types.text import TextColumn
from scrapers.columns.types.tyre import TyreColumn
from scrapers.columns.types.url import UrlColumn
from scrapers.headers_shared import BASE_METRIC_HEADERS_TO_KEYS
from scrapers.headers_shared import POINTS_HEADER
from scrapers.headers_shared import POINTS_HEADER_TO_KEY
from scrapers.section.config.driver_results import DriverResultsSectionConfig
from scrapers.section.critical import CriticalSection
from scrapers.wiki.parsers.sections.helpers import DOMAIN_SECTION_PROFILES

COMPLETE_RESULTS_REQUIRED_HEADER = "Year"

UNKNOWN_VALUE = "unknown"

SECTION_RESULT_KEYS = ("section_id", "section_label", "records", "metadata")

CAREER_HIGHLIGHTS_REQUIRED_HEADERS = frozenset(
    {"Season", "Series", "Position", "Team", "Car"},
)
CAREER_SUMMARY_REQUIRED_HEADERS = frozenset({"Season", "Series", "Position"})

DOMAIN_SECTION_ALIASES: dict[str, dict[str, set[str]]] = {
    domain: {key: set(values) for key, values in profile.heading_aliases.items()}
    for domain, profile in DOMAIN_SECTION_PROFILES.items()
}

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

COMMON_SECTION_ALIASES: dict[str, set[str]] = {
    "results": {"result", "results and standings", "grands prix"},
    "career results": {
        "racing record",
        "career record",
        "motorsport career results",
        "racing career",
    },
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

DOMAIN_SECTION_RESOLVER_CONFIG: dict[str, tuple[CriticalSection, ...]] = {
    "drivers": (
        CriticalSection(
            section_id="Career_results",
            alternative_section_ids=(
                "Career-results",
                "Career/results",
                "Racing_record",
                "Karting_record",
                "Motorsport_career_results",
                "Career_record",
                "Racing_career",
                "Formula_One_career",
                "F1_career_results",
                "Formula_One/World_Championship_results",
                "Formula_One_World_Championship_results",
                "Formula-One_World_Championship_results",
            ),
        ),
        CriticalSection(
            section_id="Non-championship",
            alternative_section_ids=(
                "Non_championship",
                "Non/championship",
                "Non-championship_races",
                "Non_championship_races",
                "Non_Championship",
                "Formula_One_non-championship_results",
            ),
        ),
    ),
    "constructors": (
        CriticalSection(
            section_id="Constructors",
            alternative_section_ids=(
                "Constructors_for_2024",
                "Constructors-for-the-current-season",
                "Teams",
                "Constructors'_Championship",
                "Current_constructors",
                "Current_teams",
                "Constructors_for_the_current_season",
            ),
        ),
        CriticalSection(
            section_id="Championship_results",
            alternative_section_ids=(
                "Championship-results",
                "Championship/results",
                "Formula_One/World_Championship_results",
                "Formula_One_World_Championship_results",
                "Formula-One_World_Championship_results",
                "World_Championship_results",
            ),
        ),
        CriticalSection(
            section_id="Complete_Formula_One_results",
            alternative_section_ids=(
                "Complete_Formula-One_results",
                "Complete_Formula_One/results",
                "Complete_World_Championship_results",
                "Complete_Formula_One/World_Championship_results",
                "Complete_Formula_One_World_Championship_results",
                "Complete_Formula-One_results",
            ),
        ),
        CriticalSection(
            section_id="History",
            alternative_section_ids=(
                "Team-History",
                "Team/History",
                "Team_history",
                "Racing_history",
                "Background",
            ),
        ),
    ),
    "circuits": (
        CriticalSection(
            section_id="Circuits",
            alternative_section_ids=(
                "F1_circuits",
                "Formula-One_circuits",
                "Current_circuits",
                "Active_circuits",
                "Formula_One_circuits",
                "List_of_Formula_One_circuits",
                "Current_Formula_One_circuits",
            ),
        ),
        CriticalSection(
            section_id="Layout_history",
            alternative_section_ids=(
                "Layout-history",
                "Layout/history",
                "History",
                "Circuit_layouts",
                "Track_layout",
                "Layout",
            ),
        ),
        CriticalSection(
            section_id="Lap_records",
            alternative_section_ids=(
                "Lap-records",
                "Lap/records",
                "Formula_One_lap_records",
                "Lap_record",
                "Official_lap_records",
                "Formula-One_lap_records",
            ),
        ),
        CriticalSection(
            section_id="Events",
            alternative_section_ids=(
                "Race_events",
                "Events/races",
                "Races",
                "Major_events",
                "Formula_One_Grands_Prix",
                "Formula_One/Grands_Prix",
            ),
        ),
    ),
    "seasons": (
        CriticalSection(
            section_id="Calendar",
            alternative_section_ids=(
                "Race-calendar",
                "Calendar/season",
                "Season_calendar",
                "Race_calendar",
                "Grands_Prix",
                "Championship_calendar",
                "World_Championship_calendar",
            ),
        ),
        CriticalSection(
            section_id="World_Drivers'_Championship_standings",
            alternative_section_ids=(
                "WDC_standings",
                "World-Drivers-Championship-standings",
                "World_Championship_of_Drivers_standings",
                "Drivers'_Championship_standings",
                "Drivers_standings",
                "World_Drivers_Championship_standings",
            ),
        ),
        CriticalSection(
            section_id="World_Constructors'_Championship_standings",
            alternative_section_ids=(
                "WCC_standings",
                "World-Constructors-Championship-standings",
                "International_Cup_for_F1_Constructors_standings",
                "Constructors'_Championship_standings",
                "Constructors_standings",
                "World_Constructors_Championship_standings",
            ),
        ),
        CriticalSection(
            section_id="Non-championship",
            alternative_section_ids=(
                "Non_championship",
                "Non/championship",
                "Non-championship_races",
                "Non_championship_races",
                "Non-championship_events",
                "Non_Championship",
            ),
        ),
    ),
    "grands_prix": (
        CriticalSection(
            section_id="By_year",
            alternative_section_ids=(
                "By-year",
                "By/year",
                "Winners",
                "Results_by_year",
                "By_season",
                "By_Year",
                "By_year:_the_European_Grand_Prix_as_a_standalone_event",
                "By_year_-_the_European_Grand_Prix_as_a_standalone_event",
                "Winners_of_the_Caesars_Palace_Grand_Prix",
            ),
        ),
        CriticalSection(
            section_id="Red-flagged_races",
            alternative_section_ids=(
                "Red_flagged-races",
                "Red-flagged/races",
                "List_of_red-flagged_Formula_One_World_Championship_races",
                "Formula_One_World_Championship_red-flagged_races",
                "Formula_One/World_Championship_red-flagged_races",
                "List_of_red_flagged_Formula_One_World_Championship_races",
                "Red_flagged_races",
            ),
        ),
        CriticalSection(
            section_id="Non-championship_races",
            alternative_section_ids=(
                "Non_championship-races",
                "Non-championship/races",
                "List_of_red-flagged_non-championship_Formula_One_races",
                "List_of_red_flagged_non-championship_Formula_One_races",
                "Red-flagged_non-championship_races",
                "Non-championship_red-flagged_races",
            ),
        ),
    ),
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
