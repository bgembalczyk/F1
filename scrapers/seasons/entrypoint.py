"""Domain facade for launching the seasons list scraper."""

from pathlib import Path

from scrapers.base.helpers.runner import run_and_export
from scrapers.base.run_config import RunConfig
from scrapers.seasons.list_scraper import SeasonsListScraper

LIST_SCRAPER_CLASS = SeasonsListScraper
DEFAULT_OUTPUT_JSON = "seasons/f1_seasons.json"
DEFAULT_OUTPUT_CSV = "seasons/f1_seasons.csv"


def run_list_scraper(*, run_config: RunConfig | None = None) -> None:
    """Run the canonical seasons list scraping entrypoint."""
    run_and_export(
        LIST_SCRAPER_CLASS,
        DEFAULT_OUTPUT_JSON,
        DEFAULT_OUTPUT_CSV,
        run_config=run_config
        or RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
        ),
    )
