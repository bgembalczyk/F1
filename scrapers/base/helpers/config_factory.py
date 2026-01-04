from dataclasses import dataclass

from scrapers.base.options import ScraperOptions


@dataclass(frozen=True)
class ScraperCommonConfig:
    include_urls: bool = True
    normalize_empty_values: bool = True
    validation_mode: str = "soft"


def _apply_common_config(
    options: ScraperOptions,
    config: ScraperCommonConfig,
) -> ScraperOptions:
    options.include_urls = config.include_urls
    options.normalize_empty_values = config.normalize_empty_values
    options.validation_mode = config.validation_mode
    return options


def build_table_config(
    options: ScraperOptions | None = None,
    *,
    config: ScraperCommonConfig | None = None,
) -> ScraperOptions:
    resolved = options or ScraperOptions()
    resolved_config = config or ScraperCommonConfig()
    return _apply_common_config(resolved, resolved_config)


def build_list_config(
    options: ScraperOptions | None = None,
    *,
    config: ScraperCommonConfig | None = None,
) -> ScraperOptions:
    resolved = options or ScraperOptions()
    resolved_config = config or ScraperCommonConfig()
    return _apply_common_config(resolved, resolved_config)
