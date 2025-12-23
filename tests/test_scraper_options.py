import pytest

from scrapers.base.options import ScraperOptions, HttpPolicy


def test_scraper_options_uses_default_policy_when_none_provided():
    options = ScraperOptions()
    
    assert options.policy is not None
    assert options.policy.timeout == 10
    assert options.policy.retries == 0


def test_scraper_options_uses_provided_policy():
    policy = HttpPolicy(timeout=5, retries=2)
    options = ScraperOptions(policy=policy)
    
    assert options.policy.timeout == 5
    assert options.policy.retries == 2


def test_http_policy_rejects_non_positive_timeout():
    with pytest.raises(ValueError):
        HttpPolicy(timeout=0)

    with pytest.raises(ValueError):
        HttpPolicy(timeout=-1)


def test_http_policy_rejects_negative_retries():
    with pytest.raises(ValueError):
        HttpPolicy(retries=-1)


def test_scraper_options_to_http_policy():
    policy = HttpPolicy(timeout=7, retries=3)
    options = ScraperOptions(policy=policy)

    result_policy = options.to_http_policy()
    assert result_policy.timeout == 7
    assert result_policy.retries == 3


def test_scraper_options_applies_policy_to_fetcher():
    policy = HttpPolicy(timeout=7)
    options = ScraperOptions(policy=policy)

    fetcher = options.with_fetcher()
    assert fetcher.timeout == 7
