"""Domain facade for launching the grands prix list scraper."""

from scrapers.base.domain_entrypoint import install_domain_entrypoint

install_domain_entrypoint(globals(), domain="grands_prix")
