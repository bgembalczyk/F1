from __future__ import annotations

from pathlib import Path
from types import ModuleType

import pytest

from scrapers.wiki import discovery


@pytest.mark.unit
def test_iter_discovery_module_specs_uses_configured_patterns(tmp_path, monkeypatch) -> None:
    (tmp_path / "a").mkdir()
    (tmp_path / "a" / "runner.py").touch()
    (tmp_path / "b").mkdir()
    (tmp_path / "b" / "seed.py").touch()
    (tmp_path / "ignore").mkdir()
    (tmp_path / "ignore" / "ignored.py").touch()

    monkeypatch.setattr(discovery, "_repo_root", lambda: tmp_path)
    monkeypatch.setattr(
        discovery,
        "DISCOVERY_PATTERNS",
        (
            discovery.DiscoveryPattern(glob="a/*.py", component_type="runner"),
            discovery.DiscoveryPattern(glob="b/*.py", component_type="list_scraper"),
        ),
    )

    specs = discovery._iter_discovery_module_specs()

    assert specs == (
        ("a.runner", "runner"),
        ("b.seed", "list_scraper"),
    )


@pytest.mark.unit
def test_discover_components_filters_module_by_pattern_component_type(monkeypatch) -> None:
    class _Runner:
        COMPONENT_METADATA = {
            "layer": "layer_one",
            "domain": "x",
            "seed_name": "runner_seed",
            "output_category": "x",
            "component_type": "runner",
        }

    class _ListScraper:
        COMPONENT_METADATA = {
            "layer": "layer_one",
            "domain": "x",
            "seed_name": "seed",
            "output_category": "x",
            "component_type": "list_scraper",
            "default_output_path": "raw/x/seeds/complete_x",
            "legacy_output_path": "x/complete_x",
        }

    fake_module = ModuleType("fake.module")
    fake_module._Runner = _Runner
    fake_module._ListScraper = _ListScraper

    monkeypatch.setattr(
        discovery,
        "_iter_discovery_module_specs",
        lambda: (("fake.module", "runner"),),
    )
    monkeypatch.setattr(discovery.importlib, "import_module", lambda _: fake_module)

    discovered = discovery.discover_components()

    assert [component.metadata.component_type for component in discovered] == ["runner"]


@pytest.mark.unit
def test_iter_discovery_module_paths_accepts_override_patterns(tmp_path) -> None:
    (tmp_path / "m").mkdir()
    (tmp_path / "m" / "one.py").touch()
    (tmp_path / "n").mkdir()
    (tmp_path / "n" / "two.py").touch()

    paths = discovery._iter_discovery_module_paths(
        tmp_path,
        patterns=(
            discovery.DiscoveryPattern(glob="m/*.py", component_type="runner"),
            discovery.DiscoveryPattern(glob="n/*.py", component_type="list_scraper"),
        ),
    )

    assert {path.relative_to(tmp_path) for path in paths} == {
        Path("m/one.py"),
        Path("n/two.py"),
    }
