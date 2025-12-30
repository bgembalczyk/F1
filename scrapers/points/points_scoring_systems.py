from pathlib import Path

from scrapers.base.runner import RunConfig, run_and_export
from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.skip import SkipColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.scraper import F1TableScraper

HISTORICAL_POSITIONS = [
    "1st",
    "2nd",
    "3rd",
    "4th",
    "5th",
    "6th",
    "7th",
    "8th",
    "9th",
    "10th",
]

SPRINT_POSITIONS = [
    "1st",
    "2nd",
    "3rd",
    "4th",
    "5th",
    "6th",
    "7th",
    "8th",
]


class PointsScoringSystemsHistoryScraper(F1TableScraper):
    """
    Tabela: List of Formula One World Championship points scoring systems used throughout history
    https://en.wikipedia.org/wiki/List_of_Formula_One_World_Championship_points_scoring_systems
    """

    CONFIG = ScraperConfig(
        url="https://en.wikipedia.org/wiki/List_of_Formula_One_World_Championship_points_scoring_systems",
        section_id="Points_scoring_systems",
        expected_headers=[
            "Seasons",
            *HISTORICAL_POSITIONS,
            "Fastest lap",
            "Drivers' Championship",
            "Constructors' Championship",
            "Notes",
        ],
        column_map={
            "Seasons": "seasons",
            **{position: position.lower() for position in HISTORICAL_POSITIONS},
            "Fastest lap": "fastest_lap",
            "Drivers' Championship": "drivers_championship",
            "Constructors' Championship": "constructors_championship",
            "Notes": "notes",
        },
        columns={
            "seasons": SeasonsColumn(),
            "1st": AutoColumn(),
            **{position.lower(): IntColumn() for position in HISTORICAL_POSITIONS[1:]},
            "fastest_lap": AutoColumn(),
            "drivers_championship": AutoColumn(),
            "constructors_championship": AutoColumn(),
            "notes": SkipColumn(),
        },
    )


class SprintQualifyingPointsScraper(F1TableScraper):
    """
    Tabela: Sprint qualifying and the sprints
    https://en.wikipedia.org/wiki/List_of_Formula_One_World_Championship_points_scoring_systems
    """

    CONFIG = ScraperConfig(
        url="https://en.wikipedia.org/wiki/List_of_Formula_One_World_Championship_points_scoring_systems",
        section_id="Sprint_races",
        expected_headers=[
            "Seasons",
            *SPRINT_POSITIONS,
        ],
        column_map={
            "Seasons": "seasons",
            **{position: position.lower() for position in SPRINT_POSITIONS},
        },
        columns={
            "seasons": SeasonsColumn(),
            **{position.lower(): IntColumn() for position in SPRINT_POSITIONS},
        },
    )


class ShortenedRacePointsScraper(F1TableScraper):
    """
    Tabela: Shortened race points criteria
    https://en.wikipedia.org/wiki/List_of_Formula_One_World_Championship_points_scoring_systems
    """

    CONFIG = ScraperConfig(
        url="https://en.wikipedia.org/wiki/List_of_Formula_One_World_Championship_points_scoring_systems",
        section_id="Shortened_races",
        expected_headers=[
            "Seasons",
            "Race length completed",
            *HISTORICAL_POSITIONS,
            "Fastest lap",
            "Notes",
        ],
        column_map={
            "Seasons": "seasons",
            "Race length completed": "race_length_completed",
            **{position: position.lower() for position in HISTORICAL_POSITIONS},
            "Fastest lap": "fastest_lap",
            "Notes": "notes",
        },
        columns={
            "seasons": SeasonsColumn(),
            "race_length_completed": TextColumn(),
            **{position.lower(): AutoColumn() for position in HISTORICAL_POSITIONS},
            "fastest_lap": AutoColumn(),
            "notes": SkipColumn(),
        },
    )


if __name__ == "__main__":
    run_and_export(
        PointsScoringSystemsHistoryScraper,
        "points/points_scoring_systems_history.json",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
        ),
    )
    run_and_export(
        SprintQualifyingPointsScraper,
        "points/points_scoring_systems_sprint.json",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
        ),
    )
    run_and_export(
        ShortenedRacePointsScraper,
        "points/points_scoring_systems_shortened.json",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
        ),
    )
