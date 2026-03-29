from dataclasses import dataclass

from scrapers.base.options import ScraperOptions
from scrapers.base.run_config import RunConfig

RUN_CONFIG_TO_OPTIONS_FIELD_MAP: tuple[tuple[str, str], ...] = (
    ("debug_dir", "debug_dir"),
    ("cache_dir", "cache_dir"),
    ("cache_ttl", "cache_ttl"),
    ("cache_adapter", "cache_adapter"),
    ("http_timeout", "http_timeout"),
    ("http_retries", "http_retries"),
    ("http_backoff_seconds", "http_backoff_seconds"),
)


def run_config_to_scraper_options(
    *,
    run_config: RunConfig,
    run_id: str,
    base_options: ScraperOptions | None = None,
    supports_urls: bool = True,
) -> ScraperOptions:
    """Build ScraperOptions from RunConfig using one explicit mapping path."""
    options = base_options or run_config.options or ScraperOptions()

    for run_field, option_field in RUN_CONFIG_TO_OPTIONS_FIELD_MAP:
        value = getattr(run_config, run_field)
        if value is not None:
            setattr(options, option_field, value)

    if supports_urls:
        options.include_urls = run_config.include_urls

    options.run_id = run_id
    options.quality_report = run_config.quality_report
    options.error_report = run_config.error_report
    return options


@dataclass(frozen=True)
class RunConfigOptionsMapper:
    """Backward-compatible adapter over run_config_to_scraper_options."""

    def apply(
        self,
        *,
        run_config: RunConfig,
        options: ScraperOptions,
        run_id: str,
        supports_urls: bool = True,
    ) -> ScraperOptions:
        return run_config_to_scraper_options(
            run_config=run_config,
            run_id=run_id,
            base_options=options,
            supports_urls=supports_urls,
        )
