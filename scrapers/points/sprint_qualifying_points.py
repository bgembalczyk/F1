from scrapers.base.helpers.runner import run_and_export
from scrapers.base.records import record_from_mapping
from scrapers.base.run_config import RunConfig
from scrapers.base.table.config import ScraperConfig
from scrapers.points.base_points_scraper import BasePointsScraper
from scrapers.points.constants import SPRINT_QUALIFYING_EXPECTED_HEADERS
from scrapers.points.schemas import build_sprint_qualifying_schema


class SprintQualifyingPointsScraper(BasePointsScraper):
    """
    Tabela: Sprint qualifying and the sprints
    https://en.wikipedia.org/wiki/List_of_Formula_One_World_Championship_points_scoring_systems
    """

    CONFIG = ScraperConfig(
        url=BasePointsScraper.BASE_URL,
        section_id="Sprint_races",
        expected_headers=SPRINT_QUALIFYING_EXPECTED_HEADERS,
        schema=build_sprint_qualifying_schema(),
        record_factory=record_from_mapping,
    )


def run_list_scraper(*, run_config: RunConfig) -> None:
    run_and_export(
        SprintQualifyingPointsScraper,
        "points/points_scoring_systems_sprint.json",
        run_config=run_config,
    )

if __name__ == "__main__":
    from scrapers.cli import run_legacy_wrapper

    run_legacy_wrapper("scrapers.points.sprint_qualifying_points")
