from pathlib import Path

from scrapers.base.helpers.runner import run_and_export
from scrapers.base.options import ScraperOptions
from scrapers.base.records import record_from_mapping
from scrapers.base.runner import RunConfig
from scrapers.base.table.config import ScraperConfig
from scrapers.base.transformers.shortened_race_points import ShortenedRacePointsTransformer
from scrapers.points.base_points_scraper import BasePointsScraper
from scrapers.points.constants import SHORTENED_RACE_EXPECTED_HEADERS
from scrapers.points.schemas import build_shortened_race_points_schema
from scrapers.points.spec import POINTS_LIST_SPEC
from scrapers.points.spec import build_points_list_config


class ShortenedRacePointsScraper(BasePointsScraper):
    options_domain = POINTS_LIST_SPEC.domain
    options_profile = POINTS_LIST_SPEC.options_profile

    CONFIG = build_points_list_config(
        section_id="Shortened_races",
        expected_headers=SHORTENED_RACE_EXPECTED_HEADERS,
        schema=build_shortened_race_points_schema(),
        record_factory=record_from_mapping,
    )

    def __init__(self, *, options: ScraperOptions | None = None, config: ScraperConfig | None = None) -> None:
        options = options or ScraperOptions()
        options.transformers = [*list(options.transformers or []), ShortenedRacePointsTransformer()]
        super().__init__(options=options, config=config)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--quality-report", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--error-report", action=argparse.BooleanOptionalAction, default=False)
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
