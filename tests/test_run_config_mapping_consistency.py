from scrapers.base.factory.run_config_options_mapper import (
    RUN_CONFIG_TO_OPTIONS_FIELD_MAP,
)
from scrapers.base.factory.run_config_options_mapper import run_config_to_scraper_options
from scrapers.base.run_config import RunConfig


def test_run_config_to_scraper_options_has_unique_transformation_paths() -> None:
    run_fields = [run_field for run_field, _ in RUN_CONFIG_TO_OPTIONS_FIELD_MAP]
    option_fields = [option_field for _, option_field in RUN_CONFIG_TO_OPTIONS_FIELD_MAP]

    assert len(run_fields) == len(set(run_fields))
    assert len(option_fields) == len(set(option_fields))


def test_run_config_to_scraper_options_maps_each_declared_field() -> None:
    run_config = RunConfig(
        debug_dir="debug",
        cache_dir="cache",
        cache_ttl=11,
        cache_adapter="adapter",
        http_timeout=22,
        http_retries=3,
        http_backoff_seconds=1.5,
        include_urls=False,
        quality_report=True,
        error_report=True,
    )

    options = run_config_to_scraper_options(run_config=run_config, run_id="run-xyz")

    assert options.debug_dir == "debug"
    assert options.cache_dir == "cache"
    assert options.cache_ttl == 11
    assert options.cache_adapter == "adapter"
    assert options.http_timeout == 22
    assert options.http_retries == 3
    assert options.http_backoff_seconds == 1.5
    assert options.include_urls is False
    assert options.quality_report is True
    assert options.error_report is True
    assert options.run_id == "run-xyz"
