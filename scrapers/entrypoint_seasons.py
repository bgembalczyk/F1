"""Domain facade for launching the seasons list scraper."""

from scrapers.domain_entrypoint_service import install_domain_entrypoint

install_domain_entrypoint(globals(), domain="seasons")
