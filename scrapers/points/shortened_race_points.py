from scrapers.base.helpers.runner import run_and_export
from scrapers.base.options import ScraperOptions
from scrapers.base.records import record_from_mapping
from scrapers.base.run_config import RunConfig
from scrapers.base.table.config import TableScraperConfig
from scrapers.base.transformers.shortened_race_points import (
    ShortenedRacePointsTransformer,
)
from scrapers.points.base_points_scraper import BasePointsScraper
from scrapers.points.constants import SHORTENED_RACE_EXPECTED_HEADERS
from scrapers.points.schemas import build_shortened_race_points_schema


class ShortenedRacePointsScraper(BasePointsScraper):
    """
    Tabela: Shortened race points criteria
    https://en.wikipedia.org/wiki/List_of_Formula_One_World_Championship_points_scoring_systems
    """

    CONFIG = TableScraperConfig(
        url=BasePointsScraper.BASE_URL,
        section_id="Shortened_races",
        expected_headers=SHORTENED_RACE_EXPECTED_HEADERS,
        schema=build_shortened_race_points_schema(),
        record_factory=record_from_mapping,
    )

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        config: TableScraperConfig | None = None,
    ) -> None:
        options = options or ScraperOptions()
        options.transformers = [
            *list(options.transformers or []),
            ShortenedRacePointsTransformer(),
        ]
        super().__init__(options=options, config=config)


def run_list_scraper(*, run_config: RunConfig) -> None:
    run_and_export(
        ShortenedRacePointsScraper,
        "points/points_scoring_systems_shortened.json",
        run_config=run_config,
    )


if __name__ == "__main__":
    from scrapers.cli import run_current_legacy_wrapper

    run_current_legacy_wrapper()
