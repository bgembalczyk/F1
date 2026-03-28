"""Domain facade for launching the drivers list scraper."""

from scrapers.base.domain_entrypoint import build_entrypoint_alias_getattr_for_domain
from scrapers.base.domain_entrypoint import build_run_list_scraper_for_domain

_DOMAIN = "drivers"
run_list_scraper = build_run_list_scraper_for_domain(_DOMAIN)
__getattr__ = build_entrypoint_alias_getattr_for_domain(_DOMAIN)
