"""Domain facade for launching the seasons list scraper."""

from scrapers.base.domain_entrypoint import build_run_list_scraper
from scrapers.base.domain_entrypoint import minimal_profile
from scrapers.seasons.list_scraper import SeasonsListScraper

LIST_SCRAPER_CLASS = SeasonsListScraper
DEFAULT_OUTPUT_JSON = "seasons/f1_seasons.json"
DEFAULT_OUTPUT_CSV = "seasons/f1_seasons.csv"
RUN_CONFIG_PROFILE = minimal_profile

run_list_scraper = build_run_list_scraper(
    list_scraper_cls=LIST_SCRAPER_CLASS,
    default_output_json=DEFAULT_OUTPUT_JSON,
    default_output_csv=DEFAULT_OUTPUT_CSV,
    default_profile=RUN_CONFIG_PROFILE,
)
