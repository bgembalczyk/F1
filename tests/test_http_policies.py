# ruff: noqa: E501, PLR2004, RUF001, RUF002, RUF003, SLF001, ARG001, ARG002, N802, B017, PT011, PT017, E402, PT001, PLC0415, RUF100
from dataclasses import fields
from scrapers.base.options import ScraperOptions
from scrapers.base.run_config import RunConfig
from scrapers.base.runner import RUN_CONFIG_OPTION_FIELD_MAP
from scrapers.base.runner import ScraperRunner


def test_scraper_options_overrides_http_policy() -> None:
    options = ScraperOptions(http_timeout=25, http_retries=2)

    policy = options.to_http_policy()

    assert policy.timeout == 25
    assert policy.retries == 2


def test_scraper_options_backoff_maps_to_http_client_config() -> None:
    options = ScraperOptions(http_backoff_seconds=1.25)

    fetcher = options.with_fetcher()

    assert fetcher.http_client.config.backoff_seconds == 1.25


def test_run_config_http_overrides_map_to_options() -> None:
    class DummyScraper:
        def __init__(self, *, options: ScraperOptions) -> None:
            self.options = options

        def fetch(self):
            return []

    run_config = RunConfig(
        http_timeout=18,
        http_retries=3,
        http_backoff_seconds=2.5,
    )

    runner = ScraperRunner(run_config)
    scraper = runner._make_scraper(DummyScraper, run_id="test-run")

    policy = scraper.options.to_http_policy()
    assert policy.timeout == 18
    assert policy.retries == 3

    fetcher = scraper.options.with_fetcher()
    assert fetcher.http_client.config.backoff_seconds == 2.5


def test_run_config_to_options_field_map_stays_in_sync() -> None:
    run_config_fields = {field.name for field in fields(RunConfig)}
    scraper_option_fields = {field.name for field in fields(ScraperOptions)}

    shared_fields = run_config_fields & scraper_option_fields
    special_fields = {
        "include_urls",
        "output_dir",
        "scraper_kwargs",
        "options",
        "quality_report",
        "error_report",
    }

    expected_mapped_fields = shared_fields - special_fields
    mapped_fields = {run_attr for run_attr, _ in RUN_CONFIG_OPTION_FIELD_MAP}

    assert mapped_fields == expected_mapped_fields


def test_build_options_copies_only_non_none_values_from_run_config() -> None:
    existing_options = ScraperOptions(
        debug_dir=None,
        cache_dir="from-options-cache",
        cache_ttl=17,
        cache_adapter="adapter-from-options",
        http_timeout=55,
        http_retries=9,
        http_backoff_seconds=7.5,
    )
    run_config = RunConfig(
        options=existing_options,
        debug_dir="from-run-config-debug",
        cache_dir=None,
        cache_ttl=99,
        cache_adapter=None,
        http_timeout=12,
        http_retries=None,
        http_backoff_seconds=1.25,
    )

    runner = ScraperRunner(run_config)
    options = runner._build_options(run_id="run-123")

    assert options is existing_options
    assert options.run_id == "run-123"
    assert options.debug_dir == "from-run-config-debug"
    assert options.cache_dir == "from-options-cache"
    assert options.cache_ttl == 99
    assert options.cache_adapter == "adapter-from-options"
    assert options.http_timeout == 12
    assert options.http_retries == 9
    assert options.http_backoff_seconds == 1.25
