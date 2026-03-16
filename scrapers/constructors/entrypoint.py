"""Domain facade for launching the constructors list scraper."""

from pathlib import Path

from scrapers.base.helpers.runner import run_and_export
from scrapers.base.run_config import RunConfig
from scrapers.constructors.current_constructors_list import CURRENT_YEAR
from scrapers.constructors.current_constructors_list import CurrentConstructorsListScraper

LIST_SCRAPER_CLASS = CurrentConstructorsListScraper
DEFAULT_OUTPUT_JSON = f"constructors/f1_constructors_{CURRENT_YEAR}.json"
DEFAULT_OUTPUT_CSV = f"constructors/f1_constructors_{CURRENT_YEAR}.csv"


def run_list_scraper(*, run_config: RunConfig | None = None) -> None:
    """Run the canonical constructors list scraping entrypoint."""
    run_and_export(
        LIST_SCRAPER_CLASS,
        DEFAULT_OUTPUT_JSON,
        DEFAULT_OUTPUT_CSV,
        run_config=run_config
        or RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
            debug_dir=Path("../../data/debug"),
        ),
    )
