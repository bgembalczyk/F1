from pathlib import Path

from scrapers.base.runner import RunConfig
from scrapers.base.runner import run_and_export
from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.skip import SkipColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.scraper import F1TableScraper
from scrapers.points.constants import HISTORICAL_POSITIONS


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


if __name__ == "__main__":
    run_and_export(
        PointsScoringSystemsHistoryScraper,
        "points/points_scoring_systems_history.json",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
        ),
    )
