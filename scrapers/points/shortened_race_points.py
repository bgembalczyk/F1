from pathlib import Path

from scrapers.base.helpers.runner import run_and_export
from scrapers.base.records import record_from_mapping
from scrapers.base.runner import RunConfig
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.scraper import F1TableScraper
from scrapers.base.transformers import RecordTransformer
from scrapers.points.constants import (
    FASTEST_LAP_HEADER,
    HISTORICAL_POSITIONS,
    NOTES_HEADER,
    RACE_LENGTH_COMPLETED_HEADER,
    SEASONS_HEADER,
    SHORTENED_RACE_EXPECTED_HEADERS,
)
from scrapers.points.schemas import build_shortened_race_points_schema
from scrapers.base.transformers.shortened_race_points import (
    ShortenedRacePointsTransformer,
)


class ShortenedRacePointsScraper(F1TableScraper):
    """
    Tabela: Shortened race points criteria
    https://en.wikipedia.org/wiki/List_of_Formula_One_World_Championship_points_scoring_systems
    """

    CONFIG = ScraperConfig(
        url="https://en.wikipedia.org/wiki/List_of_Formula_One_World_Championship_points_scoring_systems",
        section_id="Shortened_races",
        expected_headers=SHORTENED_RACE_EXPECTED_HEADERS,
        schema=build_shortened_race_points_schema(),
        record_factory=record_from_mapping,
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.transformers = [ShortenedRacePointsTransformer()]


if __name__ == "__main__":
    run_and_export(
        ShortenedRacePointsScraper,
        "points/points_scoring_systems_shortened.json",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
        ),
    )
