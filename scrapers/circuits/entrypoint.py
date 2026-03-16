"""Domain facade for launching the circuits list scraper."""

from pathlib import Path

from scrapers.base.helpers.runner import run_and_export
from scrapers.base.run_config import RunConfig
from scrapers.circuits.list_scraper import CircuitsListScraper

LIST_SCRAPER_CLASS = CircuitsListScraper
DEFAULT_OUTPUT_JSON = "circuits/f1_circuits.json"
DEFAULT_OUTPUT_CSV = "circuits/f1_circuits.csv"


def run_list_scraper(*, run_config: RunConfig | None = None) -> None:
    """Run the canonical circuits list scraping entrypoint."""
    run_and_export(
        LIST_SCRAPER_CLASS,
        DEFAULT_OUTPUT_JSON,
        DEFAULT_OUTPUT_CSV,
        run_config=run_config
        or RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
            debug_dir=Path("../../data/debug"),
            quality_report=True,
            error_report=False,
        ),
    )
