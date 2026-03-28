import pytest

from infrastructure.http_client.caching.wiki import WikipediaCachePolicy
from scrapers.base.options import HttpPolicy
from scrapers.base.options import default_http_policy
from scrapers.base.table import config as table_config_module
from scrapers.config import default_config
from scrapers import config as runtime_config_module
from scrapers.config import default_scraper_config
from scrapers.config import RuntimeScraperConfig
from scrapers.data_paths import DataPaths
from scrapers.data_paths import default_data_paths

DEFAULT_TIMEOUT = 10


def test_http_policy_rejects_invalid_values():
    with pytest.raises(ValueError, match="timeout must be greater than 0"):
        HttpPolicy(timeout=0)

    with pytest.raises(ValueError, match="retries must be >= 0"):
        HttpPolicy(retries=-1)


def test_default_http_policy_builds_wikipedia_cache():
    policy = default_http_policy()

    assert isinstance(policy, HttpPolicy)
    assert isinstance(policy.cache, WikipediaCachePolicy)
    assert policy.timeout == DEFAULT_TIMEOUT


def test_default_scraper_config_includes_http_policy():
    config = default_scraper_config()

    assert isinstance(config, RuntimeScraperConfig)
    assert config.include_urls is True
    assert isinstance(config.policy, HttpPolicy)


def test_default_config_is_scraper_config_alias():
    first = default_config()
    second = default_scraper_config()

    assert isinstance(first, RuntimeScraperConfig)
    assert isinstance(second, RuntimeScraperConfig)
    assert first is not second


def test_default_data_paths_and_compatibility_resolution(tmp_path):
    paths = default_data_paths(base_dir=tmp_path / "data")

    assert isinstance(paths, DataPaths)
    assert paths.raw == tmp_path / "data" / "raw"
    assert paths.normalized == tmp_path / "data" / "normalized"
    assert paths.checkpoints == tmp_path / "data" / "checkpoints"

    legacy = paths.legacy_wiki_file("drivers", "f1_drivers.json")
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_text("[]", encoding="utf-8")

    resolved = paths.resolve_compatible_input("drivers", "f1_drivers.json")
    assert resolved == legacy


def test_deprecated_runtime_scraper_config_alias_warns():
    with pytest.deprecated_call(
        match="ScraperConfig is deprecated; use RuntimeScraperConfig instead.",
    ):
        runtime_config_module.ScraperConfig()


def test_deprecated_table_scraper_config_alias_warns():
    with pytest.deprecated_call(
        match="ScraperConfig is deprecated; use TableScraperConfig instead.",
    ):
        table_config_module.ScraperConfig(url="https://example.com")
