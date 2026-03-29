"""Domain facade for launching the seasons list scraper."""

from scrapers.base.domain_entrypoint import install_domain_entrypoint

install_domain_entrypoint(globals(), domain="seasons")
