"""Domain facade for launching the drivers list scraper."""

from scrapers.base.domain_entrypoint import build_run_list_scraper
from scrapers.base.domain_entrypoint import strict_quality_profile
from scrapers.drivers.list_scraper import F1DriversListScraper

LIST_SCRAPER_CLASS = F1DriversListScraper
DEFAULT_OUTPUT_JSON = "drivers/f1_drivers.json"
RUN_CONFIG_PROFILE = strict_quality_profile

run_list_scraper = build_run_list_scraper(
    list_scraper_cls=LIST_SCRAPER_CLASS,
    default_output_json=DEFAULT_OUTPUT_JSON,
    default_profile=RUN_CONFIG_PROFILE,
)
