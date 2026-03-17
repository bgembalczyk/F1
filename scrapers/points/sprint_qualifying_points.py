from pathlib import Path

from scrapers.base.helpers.runner import run_and_export
from scrapers.base.records import record_from_mapping
from scrapers.base.runner import RunConfig
from scrapers.base.table.config import ScraperConfig
from scrapers.points.base_points_scraper import BasePointsScraper
from scrapers.points.constants import SPRINT_QUALIFYING_EXPECTED_HEADERS
from scrapers.points.schemas import build_sprint_qualifying_schema
from scrapers.points.spec import POINTS_LIST_SPEC
from scrapers.points.spec import build_points_list_config


class SprintQualifyingPointsScraper(BasePointsScraper):
    options_domain = POINTS_LIST_SPEC.domain
    options_profile = POINTS_LIST_SPEC.options_profile

    CONFIG = build_points_list_config(
        section_id="Sprint_races",
        expected_headers=SPRINT_QUALIFYING_EXPECTED_HEADERS,
        schema=build_sprint_qualifying_schema(),
        record_factory=record_from_mapping,
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--quality-report", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--error-report", action=argparse.BooleanOptionalAction, default=False)
    args = parser.parse_args()
    run_and_export(
        SprintQualifyingPointsScraper,
        "points/points_scoring_systems_sprint.json",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
            debug_dir=Path("../../data/debug"),
            quality_report=args.quality_report,
            error_report=args.error_report,
        ),
    )
