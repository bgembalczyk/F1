from typing import Any

from scrapers.base.helpers.common_config import ScraperCommonConfig
from scrapers.base.options import ScraperOptions
from scrapers.base.pipeline_profiles import apply_scraper_pipeline_bindings
from scrapers.base.pipeline_profiles import resolve_profile_config

DEFAULT_CONFIG_PROFILE = "seed_soft"


def apply_common_config(
    options: ScraperOptions,
    config: ScraperCommonConfig,
) -> ScraperOptions:
    options.include_urls = config.include_urls
    options.normalize_empty_values = config.normalize_empty_values
    options.validation_mode = config.validation_mode
    return options


def build_config(
    options: ScraperOptions | None = None,
    *,
    config: ScraperCommonConfig | None = None,
    domain: str | None = None,
    profile: str = DEFAULT_CONFIG_PROFILE,
) -> ScraperOptions:
    resolved = options or ScraperOptions()
    resolved_config = config or resolve_profile_config(domain=domain, profile=profile)
    return apply_common_config(resolved, resolved_config)


def build_scraper_options(
    *,
    domain: str | None,
    profile: str,
    options: ScraperOptions | None = None,
    scraper_cls: type[Any] | None = None,
) -> ScraperOptions:
    resolved = build_config(options=options, domain=domain, profile=profile)
    if scraper_cls is None:
        return resolved
    return apply_scraper_pipeline_bindings(resolved, scraper_cls=scraper_cls)
