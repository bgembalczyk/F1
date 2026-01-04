from scrapers.base.options import ScraperOptions
from scrapers.base.runner import ScraperRunner
from scrapers.base.run_config import RunConfig


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
