import pytest

from infrastructure.http_client.caching import WikipediaCachePolicy
from scrapers.base.options import HttpPolicy
from scrapers.base.options import default_http_policy
from scrapers.config import DataPaths
from scrapers.config import ScraperConfig
from scrapers.config import default_config
from scrapers.config import default_data_paths
from scrapers.config import default_scraper_config

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

    assert isinstance(config, ScraperConfig)
    assert config.include_urls is True
    assert isinstance(config.policy, HttpPolicy)


def test_default_config_is_scraper_config_alias():
    first = default_config()
    second = default_scraper_config()

    assert isinstance(first, ScraperConfig)
    assert isinstance(second, ScraperConfig)
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


def test_data_paths_domain_value_object_and_layout_policy(tmp_path):
    from scrapers.config import DomainId

    paths = DataPaths(base_dir=tmp_path / "data")

    assert str(DomainId(" Drivers ")) == "drivers"
    assert paths.raw_seed_file("drivers", "complete_drivers") == tmp_path / "data" / "raw" / "drivers" / "seeds" / "complete_drivers"
    assert paths.raw_list_file("drivers", "f1_drivers.json") == tmp_path / "data" / "raw" / "drivers" / "list" / "f1_drivers.json"
    assert paths.normalized_file("drivers", "f1_drivers.json") == tmp_path / "data" / "normalized" / "drivers" / "f1_drivers.json"
    assert paths.checkpoint_step_file(1, "layer1", "drivers") == tmp_path / "data" / "checkpoints" / "step_1_layer1_drivers.json"
    assert paths.audit_file("step_audit.json") == tmp_path / "data" / "audit" / "step_audit.json"


def test_domain_value_object_rejects_invalid_identifier():
    from scrapers.config import DomainId

    with pytest.raises(ValueError):
        DomainId("bad/domain")
