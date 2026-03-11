import pytest

from infrastructure.http_client.caching import WikipediaCachePolicy
from scrapers.base.options import HttpPolicy
from scrapers.base.options import default_http_policy
from scrapers.config import ScraperConfig
from scrapers.config import default_config
from scrapers.config import default_scraper_config


def test_http_policy_rejects_invalid_values():
    with pytest.raises(ValueError, match="timeout must be greater than 0"):
        HttpPolicy(timeout=0)

    with pytest.raises(ValueError, match="retries must be >= 0"):
        HttpPolicy(retries=-1)


def test_default_http_policy_builds_wikipedia_cache():
    policy = default_http_policy()

    assert isinstance(policy, HttpPolicy)
    assert isinstance(policy.cache, WikipediaCachePolicy)
    assert policy.timeout == 10


def test_default_scraper_config_includes_http_policy():
    config = default_scraper_config()

    assert isinstance(config, ScraperConfig)
    assert config.include_urls is True
    assert isinstance(config.policy, HttpPolicy)


def test_default_config_is_scraper_config_alias():
    first = default_config()
    second = default_scraper_config()

    assert isinstance(first, ScraperConfig)
    assert isinstance(second, ScraperConfig)
    assert first is not second
