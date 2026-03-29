from __future__ import annotations

from types import ModuleType
from typing import get_type_hints

import pytest

from scrapers.wiki.component_metadata import build_component_metadata
from scrapers.wiki.constants import COMPONENT_METADATA_ATTR
from scrapers.wiki.discovery import DiscoveredComponent
from scrapers.wiki.discovery import DiscoveredRunnerProtocol
from scrapers.wiki.discovery import _discover_components_in_module
from scrapers.wiki.discovery import build_layer_one_runner_map_discovered


def test_discovered_component_cls_is_protocol_based_type() -> None:
    cls_type = get_type_hints(DiscoveredComponent)["cls"]
    type_names = {arg.__name__ for arg in cls_type.__args__}
    assert type_names == {
        "DiscoveredRunnerClassProtocol",
        "DiscoveredListScraperClassProtocol",
    }


def test_discovery_validates_list_scraper_contract() -> None:
    module = ModuleType("fake_list_discovery")

    class _BrokenListScraper:
        CONFIG = object()

    setattr(
        _BrokenListScraper,
        COMPONENT_METADATA_ATTR,
        build_component_metadata(domain="drivers", kind="list_scraper"),
    )
    module.BrokenListScraper = _BrokenListScraper

    with pytest.raises(TypeError, match="must expose CONFIG.url"):
        _discover_components_in_module(module)


def test_build_layer_one_runner_map_discovered_returns_runner_contract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _Runner:
        def run(self, seed, run_config, base_wiki_dir) -> None:  # noqa: ANN001
            return None

    setattr(
        _Runner,
        COMPONENT_METADATA_ATTR,
        build_component_metadata(domain="drivers", kind="runner"),
    )
    component = DiscoveredComponent(
        cls=_Runner,
        metadata=build_component_metadata(domain="drivers", kind="runner"),
    )
    monkeypatch.setattr(
        "scrapers.wiki.discovery.discover_components",
        lambda: (component,),
    )

    runner_map = build_layer_one_runner_map_discovered()

    assert set(runner_map) == {"drivers"}
    runner = runner_map["drivers"]
    assert isinstance(runner, DiscoveredRunnerProtocol)
    assert callable(runner.run)
