"""Domain facade for launching the circuits list scraper."""

from scrapers.domain_entrypoint import install_domain_entrypoint

install_domain_entrypoint(globals(), domain="circuits")
