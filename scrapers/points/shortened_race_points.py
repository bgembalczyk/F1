from scrapers.base.helpers.runner import run_and_export
from scrapers.base.records import record_from_mapping
from scrapers.base.run_config import RunConfig
from scrapers.base.table.config import build_scraper_config
from scrapers.points.base_points_scraper import BasePointsScraper
from scrapers.points.constants import SHORTENED_RACE_EXPECTED_HEADERS
from scrapers.points.schemas import build_shortened_race_points_schema


class ShortenedRacePointsScraper(BasePointsScraper):
    """
    Tabela: Shortened race points criteria
    https://en.wikipedia.org/wiki/List_of_Formula_One_World_Championship_points_scoring_systems
    """

    options_profile = "seed_soft"
    options_domain = "points"

    CONFIG = build_scraper_config(
        url=BasePointsScraper.BASE_URL,
        section_id="Shortened_races",
        expected_headers=SHORTENED_RACE_EXPECTED_HEADERS,
        schema=build_shortened_race_points_schema(),
        record_factory=record_from_mapping,
    )

def run_list_scraper(*, run_config: RunConfig) -> None:
    run_and_export(
        ShortenedRacePointsScraper,
        "points/points_scoring_systems_shortened.json",
        run_config=run_config,
    )


if __name__ == "__main__":
    from scrapers.base.deprecated_entrypoint import run_deprecated_entrypoint

    run_deprecated_entrypoint()
