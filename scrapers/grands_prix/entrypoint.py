"""Domain facade for launching the grands prix list scraper."""

from pathlib import Path

from scrapers.base.helpers.runner import run_and_export
from scrapers.base.run_config import RunConfig
from scrapers.grands_prix.list_scraper import GrandsPrixListScraper

LIST_SCRAPER_CLASS = GrandsPrixListScraper
DEFAULT_OUTPUT_JSON = "grands_prix/f1_grands_prix_by_title.json"
DEFAULT_OUTPUT_CSV = "grands_prix/f1_grands_prix_by_title.csv"


def run_list_scraper(*, run_config: RunConfig | None = None) -> None:
    """Run the canonical grands prix list scraping entrypoint."""
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
