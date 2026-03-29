from scrapers.base.factory.record_factory import RECORD_FACTORIES
from scrapers.base.table.config import build_scraper_config
from scrapers.points.base_points_scraper import BasePointsScraper
from scrapers.points.constants import SPRINT_QUALIFYING_EXPECTED_HEADERS
from scrapers.points.schemas import build_sprint_qualifying_schema


class SprintQualifyingPointsScraper(BasePointsScraper):
    """
    Tabela: Sprint qualifying and the sprints
    https://en.wikipedia.org/wiki/List_of_Formula_One_World_Championship_points_scoring_systems
    """

    CONFIG = build_scraper_config(
        url=BasePointsScraper.BASE_URL,
        section_id="Sprint_races",
        expected_headers=SPRINT_QUALIFYING_EXPECTED_HEADERS,
        schema=build_sprint_qualifying_schema(),
        record_factory=RECORD_FACTORIES.mapping(),
    )


if __name__ == "__main__":
    from scrapers.base.deprecated_entrypoint import run_deprecated_entrypoint

    run_deprecated_entrypoint()
