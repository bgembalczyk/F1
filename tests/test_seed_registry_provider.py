# ruff: noqa: SLF001
from __future__ import annotations

from types import SimpleNamespace

from layers.seed.registry import helpers
from scrapers.wiki.component_metadata import ComponentMetadata
from scrapers.wiki.discovery import DiscoveredComponent


class _ConfigA:
    url = "https://example.test/a"


class _ConfigB:
    url = "https://example.test/b"


class _ListScraperA:
    CONFIG = _ConfigA


class _ListScraperB:
    CONFIG = _ConfigB


def _component(*, seed_name: str, cls: type[object]) -> DiscoveredComponent:
    metadata = ComponentMetadata.build_layer_one_list_scraper(
        domain=seed_name,
        seed_name=seed_name,
        default_output_path=f"raw/{seed_name}/seeds/complete_{seed_name}",
        legacy_output_path=f"{seed_name}/complete_{seed_name}",
    )
    return DiscoveredComponent(cls=cls, metadata=metadata)


def test_get_wiki_seed_registry_uses_cached_provider(monkeypatch) -> None:
    calls = {"count": 0}

    def _fake_builder() -> tuple[object, ...]:
        calls["count"] += 1
        return (SimpleNamespace(seed_name="drivers"),)

    helpers.clear_wiki_seed_registry_cache()
    monkeypatch.setattr(
        helpers,
        "_build_discovered_layer_one_seed_registry",
        _fake_builder,
    )

    first = helpers.get_wiki_seed_registry()
    second = helpers.get_wiki_seed_registry()

    assert first is second
    assert calls["count"] == 1


def test_build_discovered_seed_registry_is_deterministic(monkeypatch) -> None:
    monkeypatch.setattr(helpers, "EXPLICIT_LAYER_ONE_SEED_REGISTRY", ())
    monkeypatch.setattr(
        helpers,
        "discover_layer_one_seed_components",
        lambda: {
            "seed_b": _component(seed_name="seed_b", cls=_ListScraperB),
            "seed_a": _component(seed_name="seed_a", cls=_ListScraperA),
        },
    )

    registry = helpers._build_discovered_layer_one_seed_registry()

    assert [entry.seed_name for entry in registry] == ["seed_a", "seed_b"]
