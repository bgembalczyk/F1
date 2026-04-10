"""Compatibility shim for domain list-scraper entrypoints."""

from __future__ import annotations

import warnings

from scrapers.entrypoints.domain_entrypoint_service import (
    CurrentYearOutputPathRenderer,
    DomainEntrypointConfig,
    IdentityOutputPathRenderer,
    LazyScraperFactory,
    OutputPathRenderer,
    YearPlaceholderOutputPathRenderer,
    build_entrypoint_alias_getattr_for_domain,
    build_run_list_scraper_for_domain,
    debug_profile,
    default_profile,
    get_domain_entrypoint_config,
    get_domain_entrypoint_scraper_metadata,
    install_domain_entrypoint,
)

warnings.warn(
    "scrapers.domain_entrypoint is deprecated; use "
    "scrapers.entrypoints.domain_entrypoint_service instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "CurrentYearOutputPathRenderer",
    "DomainEntrypointConfig",
    "IdentityOutputPathRenderer",
    "LazyScraperFactory",
    "OutputPathRenderer",
    "YearPlaceholderOutputPathRenderer",
    "build_entrypoint_alias_getattr_for_domain",
    "build_run_list_scraper_for_domain",
    "debug_profile",
    "default_profile",
    "get_domain_entrypoint_config",
    "get_domain_entrypoint_scraper_metadata",
    "install_domain_entrypoint",
]
