from scrapers.base.helpers.common_config import ScraperCommonConfig
from scrapers.base.helpers.constants import COMMON_CONFIG_PROFILES
from scrapers.base.helpers.constants import DEFAULT_CONFIG_PROFILE
from scrapers.base.helpers.constants import DOMAIN_CONFIG_PROFILE_OVERRIDES
from scrapers.base.options import ScraperOptions


def _resolve_common_config(*, domain: str | None, profile: str) -> ScraperCommonConfig:
    normalized_profile = profile.strip().lower()
    if normalized_profile not in COMMON_CONFIG_PROFILES:
        msg = f"Unknown scraper config profile: {profile}"
        raise ValueError(msg)

    normalized_domain = domain.strip().lower() if domain else None
    if normalized_domain:
        domain_overrides = DOMAIN_CONFIG_PROFILE_OVERRIDES.get(normalized_domain, {})
        if normalized_profile in domain_overrides:
            return domain_overrides[normalized_profile]

    return COMMON_CONFIG_PROFILES[normalized_profile]


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
    resolved_config = config or _resolve_common_config(domain=domain, profile=profile)
    return apply_common_config(resolved, resolved_config)


def build_scraper_options(
    *,
    domain: str | None,
    profile: str,
    options: ScraperOptions | None = None,
) -> ScraperOptions:
    return build_config(options=options, domain=domain, profile=profile)
