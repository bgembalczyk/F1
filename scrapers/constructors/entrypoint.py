"""Domain facade for launching the constructors list scraper."""

from scrapers.base.domain_entrypoint import build_run_list_scraper
from scrapers.base.domain_entrypoint import minimal_debug_profile
from scrapers.constructors.current_constructors_list import CURRENT_YEAR
from scrapers.constructors.current_constructors_list import (
    CurrentConstructorsListScraper,
)

LIST_SCRAPER_CLASS = CurrentConstructorsListScraper
DEFAULT_OUTPUT_JSON = f"constructors/f1_constructors_{CURRENT_YEAR}.json"
DEFAULT_OUTPUT_CSV = f"constructors/f1_constructors_{CURRENT_YEAR}.csv"
RUN_CONFIG_PROFILE = minimal_debug_profile

run_list_scraper = build_run_list_scraper(
    list_scraper_cls=LIST_SCRAPER_CLASS,
    default_output_json=DEFAULT_OUTPUT_JSON,
    default_output_csv=DEFAULT_OUTPUT_CSV,
    default_profile=RUN_CONFIG_PROFILE,
)
