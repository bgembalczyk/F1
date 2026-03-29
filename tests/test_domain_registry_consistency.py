from __future__ import annotations

from layers.orchestration.helpers import _build_explicit_layer_one_runner_map
from scrapers.base.domain_entrypoint import get_domain_entrypoint_scraper_metadata
from scrapers.base.domain_registry import DOMAIN_REGISTRY

CORE_DOMAINS = ("drivers", "constructors", "circuits", "seasons", "grands_prix")


def test_domain_entrypoint_scraper_metadata_comes_from_domain_registry() -> None:
    expected = {
        domain: DOMAIN_REGISTRY[domain].scraper_path
        for domain in CORE_DOMAINS
    }

    assert get_domain_entrypoint_scraper_metadata() == expected


def test_layer_one_explicit_runner_map_uses_domain_registry_domains() -> None:
    explicit_map = _build_explicit_layer_one_runner_map()

    assert tuple(explicit_map) == CORE_DOMAINS


def test_domain_registry_runner_metadata_is_self_consistent() -> None:
    for domain in CORE_DOMAINS:
        metadata = DOMAIN_REGISTRY[domain].runner.component_metadata
        assert metadata is not None
        assert metadata["domain"] == domain
        assert metadata["seed_name"] == domain
        assert metadata["layer"] == "layer_one"
        assert metadata["component_type"] == "runner"
