from __future__ import annotations

from types import ModuleType

from scrapers.wiki.component_metadata import ComponentMetadata
from scrapers.wiki.discovery import _clear_component_metadata_cache
from scrapers.wiki.discovery import _discover_components_in_module


def test_discovery_does_not_mutate_imported_class_metadata() -> None:
    class _Config:
        url = "https://example.test/drivers"

    class _ListScraper:
        CONFIG = _Config
        COMPONENT_METADATA = {
            "domain": "drivers",
            "seed_name": "drivers",
            "layer": "layer_one",
            "output_category": "drivers",
            "component_type": "list_scraper",
            "default_output_path": "raw/drivers/seeds/complete_drivers",
            "legacy_output_path": "drivers/complete_drivers",
        }

    module = ModuleType("tests.fake_discovery_module")
    setattr(module, "_ListScraper", _ListScraper)

    raw_before = _ListScraper.COMPONENT_METADATA

    _clear_component_metadata_cache()
    discovered = _discover_components_in_module(module)

    assert len(discovered) == 1
    assert isinstance(discovered[0].metadata, ComponentMetadata)
    assert _ListScraper.COMPONENT_METADATA is raw_before
    assert isinstance(_ListScraper.COMPONENT_METADATA, dict)
