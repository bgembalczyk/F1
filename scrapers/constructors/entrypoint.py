"""Domain facade for launching the constructors list scraper."""

from scrapers.base.domain_entrypoint import build_entrypoint_alias_getattr_for_domain
from scrapers.base.domain_entrypoint import build_run_list_scraper_for_domain

_DOMAIN = "constructors"
run_list_scraper = build_run_list_scraper_for_domain(_DOMAIN)
__getattr__ = build_entrypoint_alias_getattr_for_domain(_DOMAIN)
