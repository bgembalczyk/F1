# ruff: noqa: E501, PLR2004, RUF001, RUF002, RUF003, SLF001, ARG001, ARG002, N802, B017, PT011, PT017, E402, PT001, PLC0415, RUF100
from scrapers.base.options import ScraperOptions
from scrapers.base.run_config import RunConfig
from scrapers.base.scraper_factory import RunConfigOptionsMapper
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


def test_run_config_mapper_applies_known_fields_explicitly() -> None:
    run_config = RunConfig(
        debug_dir="debug",
        cache_dir="cache",
        cache_ttl=12,
        cache_adapter="adapter",
        http_timeout=13,
        http_retries=2,
        http_backoff_seconds=1.5,
        quality_report=True,
        error_report=True,
    )
    options = ScraperOptions()

    RunConfigOptionsMapper().apply(run_config=run_config, options=options, run_id="rid")

    assert options.debug_dir == "debug"
    assert options.cache_dir == "cache"
    assert options.cache_ttl == 12
    assert options.cache_adapter == "adapter"
    assert options.http_timeout == 13
    assert options.http_retries == 2
    assert options.http_backoff_seconds == 1.5
    assert options.run_id == "rid"
    assert options.quality_report is True
    assert options.error_report is True


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

    RunConfigOptionsMapper().apply(
        run_config=run_config,
        options=existing_options,
        run_id="run-123",
    )
    options = existing_options

    assert options.run_id == "run-123"
    assert options.debug_dir == "from-run-config-debug"
    assert options.cache_dir == "from-options-cache"
    assert options.cache_ttl == 99
    assert options.cache_adapter == "adapter-from-options"
    assert options.http_timeout == 12
    assert options.http_retries == 9
    assert options.http_backoff_seconds == 1.25
