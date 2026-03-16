"""Domain facade for launching the drivers list scraper."""

from pathlib import Path

from scrapers.base.helpers.runner import run_and_export
from scrapers.base.run_config import RunConfig
from scrapers.drivers.list_scraper import F1DriversListScraper

LIST_SCRAPER_CLASS = F1DriversListScraper
DEFAULT_OUTPUT_JSON = "drivers/f1_drivers.json"


def run_list_scraper(*, run_config: RunConfig | None = None) -> None:
    """Run the canonical drivers list scraping entrypoint."""
    run_and_export(
        LIST_SCRAPER_CLASS,
        DEFAULT_OUTPUT_JSON,
        run_config=run_config
        or RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
            debug_dir=Path("../../data/debug"),
            quality_report=True,
            error_report=False,
        ),
    )
