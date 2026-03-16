"""Domain facade for launching the circuits list scraper."""

from scrapers.base.domain_entrypoint import build_run_list_scraper
from scrapers.base.domain_entrypoint import strict_quality_profile
from scrapers.circuits.list_scraper import CircuitsListScraper

LIST_SCRAPER_CLASS = CircuitsListScraper
DEFAULT_OUTPUT_JSON = "circuits/f1_circuits.json"
DEFAULT_OUTPUT_CSV = "circuits/f1_circuits.csv"
RUN_CONFIG_PROFILE = strict_quality_profile

run_list_scraper = build_run_list_scraper(
    list_scraper_cls=LIST_SCRAPER_CLASS,
    default_output_json=DEFAULT_OUTPUT_JSON,
    default_output_csv=DEFAULT_OUTPUT_CSV,
    default_profile=RUN_CONFIG_PROFILE,
)
