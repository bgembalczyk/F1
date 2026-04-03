from scrapers.base.factory.record_factory import RECORD_FACTORIES
from scrapers.base.helpers.transformers import append_transformer
from scrapers.base.options import ScraperOptions
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.config import build_scraper_config
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

    CONFIG = build_scraper_config(
        url=BasePointsScraper.BASE_URL,
        section_id="Shortened_races",
        expected_headers=SHORTENED_RACE_EXPECTED_HEADERS,
        schema=build_shortened_race_points_schema(),
        record_factory=RECORD_FACTORIES.mapping(),
    )

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        config: ScraperConfig | None = None,
    ) -> None:
        super().__init__(
            options=append_transformer(options, ShortenedRacePointsTransformer()),
            config=config,
        )


