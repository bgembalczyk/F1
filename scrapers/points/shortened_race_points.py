from pathlib import Path

from scrapers.base.helpers.runner import run_and_export
from scrapers.base.options import ScraperOptions
from scrapers.base.records import record_from_mapping
from scrapers.base.runner import RunConfig
from scrapers.base.table.config import ScraperConfig
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

    CONFIG = ScraperConfig(
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
        config: ScraperConfig | None = None,
    ) -> None:
        options = options or ScraperOptions()
        options.transformers = [*list(options.transformers or []), ShortenedRacePointsTransformer()]
        super().__init__(options=options, config=config)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--quality-report",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Zapisz raport jakości do debug_dir/quality_report.json.",
    )
    parser.add_argument(
        "--error-report",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Zapisz raporty błędów do debug_dir/errors.jsonl.",
    )
    args = parser.parse_args()
    run_and_export(
        ShortenedRacePointsScraper,
        "points/points_scoring_systems_shortened.json",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
            debug_dir=Path("../../data/debug"),
            quality_report=args.quality_report,
            error_report=args.error_report,
        ),
    )
