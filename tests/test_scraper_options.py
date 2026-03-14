import pytest

from scrapers.base.options import HttpPolicy
from scrapers.base.options import ScraperOptions

DEFAULT_TIMEOUT = 10
DEFAULT_RETRIES = 0
CUSTOM_TIMEOUT = 5
CUSTOM_RETRIES = 2
ALT_TIMEOUT = 7
ALT_RETRIES = 3


def test_scraper_options_uses_default_policy_when_none_provided():
    options = ScraperOptions()

    assert options.policy is not None
    assert options.policy.timeout == DEFAULT_TIMEOUT
    assert options.policy.retries == DEFAULT_RETRIES


def test_scraper_options_uses_provided_policy():
    policy = HttpPolicy(timeout=CUSTOM_TIMEOUT, retries=CUSTOM_RETRIES)
    options = ScraperOptions(policy=policy)

    assert options.policy.timeout == CUSTOM_TIMEOUT
    assert options.policy.retries == CUSTOM_RETRIES


def test_http_policy_rejects_non_positive_timeout():
    with pytest.raises(ValueError, match="timeout must be greater than 0"):
        HttpPolicy(timeout=0)

    with pytest.raises(ValueError, match="timeout must be greater than 0"):
        HttpPolicy(timeout=-1)


def test_http_policy_rejects_negative_retries():
    with pytest.raises(ValueError, match="retries must be >= 0"):
        HttpPolicy(retries=-1)


def test_scraper_options_to_http_policy():
    policy = HttpPolicy(timeout=ALT_TIMEOUT, retries=ALT_RETRIES)
    options = ScraperOptions(policy=policy)

    result_policy = options.to_http_policy()
    assert result_policy.timeout == ALT_TIMEOUT
    assert result_policy.retries == ALT_RETRIES


def test_scraper_options_applies_policy_to_fetcher():
    policy = HttpPolicy(timeout=ALT_TIMEOUT)
    options = ScraperOptions(policy=policy)

    fetcher = options.with_fetcher()
    assert fetcher.timeout == ALT_TIMEOUT
