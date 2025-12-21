import pytest

from scrapers.base.options import ScraperOptions


def test_scraper_options_rejects_non_positive_timeout():
    with pytest.raises(ValueError):
        ScraperOptions(timeout=0)

    with pytest.raises(ValueError):
        ScraperOptions(timeout=-1)


def test_scraper_options_rejects_negative_retries():
    with pytest.raises(ValueError):
        ScraperOptions(retries=-1)


def test_scraper_options_legacy_http_fields_warn_and_apply():
    with pytest.warns(DeprecationWarning):
        options = ScraperOptions(timeout=5, retries=2)

    policy = options.to_http_policy()
    assert policy.timeout == 5
    assert policy.retries == 2


def test_scraper_options_legacy_timeout_applies_to_fetcher():
    with pytest.warns(DeprecationWarning):
        options = ScraperOptions(timeout=7)

    fetcher = options.with_fetcher()
    assert fetcher.timeout == 7
