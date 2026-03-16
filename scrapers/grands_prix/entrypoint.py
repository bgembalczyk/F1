"""Domain facade for launching the grands prix list scraper."""

from scrapers.base.domain_entrypoint import build_run_list_scraper
from scrapers.base.domain_entrypoint import minimal_profile
from scrapers.grands_prix.list_scraper import GrandsPrixListScraper

LIST_SCRAPER_CLASS = GrandsPrixListScraper
DEFAULT_OUTPUT_JSON = "grands_prix/f1_grands_prix_by_title.json"
DEFAULT_OUTPUT_CSV = "grands_prix/f1_grands_prix_by_title.csv"
RUN_CONFIG_PROFILE = minimal_profile

run_list_scraper = build_run_list_scraper(
    list_scraper_cls=LIST_SCRAPER_CLASS,
    default_output_json=DEFAULT_OUTPUT_JSON,
    default_output_csv=DEFAULT_OUTPUT_CSV,
    default_profile=RUN_CONFIG_PROFILE,
)
