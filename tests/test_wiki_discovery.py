from __future__ import annotations

from types import ModuleType

import pytest

from scrapers.wiki import discovery
from scrapers.wiki.seed_registry import EXPLICIT_LAYER_ONE_SEED_REGISTRY
from scrapers.wiki.seed_registry import _build_discovered_layer_one_seed_registry


def test_discovery_validation_fails_for_runner_without_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_module = ModuleType("scrapers.fake.discovery_test")

    class NewRunner:
        pass

    NewRunner.__name__ = "NewRunner"
    NewRunner.__module__ = fake_module.__name__
    fake_module.NewRunner = NewRunner

    monkeypatch.setattr(
        discovery,
        "_iter_discovery_module_names",
        lambda: (fake_module.__name__,),
    )
    monkeypatch.setattr(discovery.importlib, "import_module", lambda _name: fake_module)

    with pytest.raises(ValueError, match="Discovery metadata missing"):
        discovery.validate_discovery_metadata_completeness()


def test_seed_registry_falls_back_to_explicit_when_discovery_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "scrapers.wiki.seed_registry.discover_layer_one_seed_components",
        dict,
    )

    registry = _build_discovered_layer_one_seed_registry()

    assert registry == EXPLICIT_LAYER_ONE_SEED_REGISTRY
