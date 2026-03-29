from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.options import ScraperOptions


def test_init_scraper_options_returns_copy_without_mutating_input() -> None:
    shared_options = ScraperOptions(
        include_urls=False,
        validation_mode="hard",
        normalize_empty_values=False,
        run_id="shared-run",
    )

    resolved = init_scraper_options(shared_options, include_urls=True)

    assert resolved is not shared_options
    assert shared_options.include_urls is False
    assert resolved.include_urls is True
    assert resolved.validation_mode == "hard"
    assert resolved.normalize_empty_values is False
    assert resolved.run_id == "shared-run"


def test_init_scraper_options_include_urls_overrides_only_include_urls_field() -> None:
    shared_options = ScraperOptions(
        include_urls=False,
        validation_mode="hard",
        normalize_empty_values=False,
        quality_report=True,
        error_policy="retry",
        error_retry_attempts=3,
    )

    resolved = init_scraper_options(shared_options, include_urls=True)

    assert resolved.include_urls is True
    assert shared_options.include_urls is False
    assert resolved.validation_mode == shared_options.validation_mode
    assert resolved.normalize_empty_values == shared_options.normalize_empty_values
    assert resolved.quality_report == shared_options.quality_report
    assert resolved.error_policy == shared_options.error_policy
    assert resolved.error_retry_attempts == shared_options.error_retry_attempts


def test_init_scraper_options_supports_shared_input_across_multiple_scrapers() -> None:
    shared_options = ScraperOptions(include_urls=False)

    first_scraper_options = init_scraper_options(shared_options, include_urls=True)
    second_scraper_options = init_scraper_options(shared_options)

    assert shared_options.include_urls is False
    assert first_scraper_options.include_urls is True
    assert second_scraper_options.include_urls is False
    assert first_scraper_options is not second_scraper_options
    assert second_scraper_options is not shared_options
