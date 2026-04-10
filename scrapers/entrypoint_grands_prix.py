"""Domain facade for launching the grands prix list scraper."""

from scrapers.entrypoints.domain_entrypoint_service import install_domain_entrypoint

install_domain_entrypoint(globals(), domain="grands_prix")
