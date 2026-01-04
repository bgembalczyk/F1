from pathlib import Path

from scrapers.base.helpers.runner import run_and_export
from scrapers.base.records import record_from_mapping
from scrapers.base.runner import RunConfig
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.scraper import F1TableScraper
from scrapers.points.constants import (
    SEASONS_HEADER,
    SPRINT_POSITIONS,
    SPRINT_QUALIFYING_EXPECTED_HEADERS,
)
from scrapers.points.schemas import build_sprint_qualifying_schema


class SprintQualifyingPointsScraper(F1TableScraper):
    """
    Tabela: Sprint qualifying and the sprints
    https://en.wikipedia.org/wiki/List_of_Formula_One_World_Championship_points_scoring_systems
    """

    CONFIG = ScraperConfig(
        url="https://en.wikipedia.org/wiki/List_of_Formula_One_World_Championship_points_scoring_systems",
        section_id="Sprint_races",
        expected_headers=SPRINT_QUALIFYING_EXPECTED_HEADERS,
        schema=build_sprint_qualifying_schema(),
        record_factory=record_from_mapping,
    )


if __name__ == "__main__":
    run_and_export(
        SprintQualifyingPointsScraper,
        "points/points_scoring_systems_sprint.json",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
        ),
    )
