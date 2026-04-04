from __future__ import annotations

import importlib
import sys
import warnings
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.parametrize("module_name", ["main"])
def test_main_import_and_entrypoint_call_path(
    monkeypatch: pytest.MonkeyPatch,
    module_name: str,
) -> None:
    calls: list[str] = []

    monkeypatch.setattr("scrapers.run_wiki_flow", lambda: calls.append("run"))
    module = importlib.reload(importlib.import_module(module_name))

    assert calls == []

    module.main()

    assert calls == ["run"]


@pytest.mark.parametrize(
    ("module_name", "scraper_name", "seed_name", "expected"),
    [
        ("layers.application", "CurrentConstructorsListScraper", "", True),
        ("layers.application", "ConstructorsListScraper", "constructors_current", True),
        (
            "layers.application",
            "ConstructorsListScraper",
            "constructors_privateer",
            False,
        ),
        ("layers.application", "ConstructorsListScraper", "", False),
        ("layers.application", "SomeOtherScraper", "", False),
        ("layers.composition", "CurrentConstructorsListScraper", "", True),
        ("layers.composition", "ConstructorsListScraper", "constructors_current", True),
        (
            "layers.composition",
            "ConstructorsListScraper",
            "constructors_privateer",
            False,
        ),
        ("layers.composition", "ConstructorsListScraper", "", False),
        ("layers.composition", "SomeOtherScraper", "", False),
    ],
)
def test_should_mirror_constructors_job(
    module_name: str,
    scraper_name: str,
    seed_name: str,
    expected: bool,  # noqa: FBT001
) -> None:
    module = importlib.import_module(module_name)
    list_scraper_cls = type(scraper_name, (), {})
    job = type("Job", (), {"list_scraper_cls": list_scraper_cls, "seed_name": seed_name})()

    assert module._should_mirror_constructors_job(job) is expected  # noqa: SLF001


@pytest.mark.parametrize(
    ("factory", "expected"),
    [
        pytest.param(
            "layers.application.create_default_wiki_pipeline_application",
            "app",
            id="application-module",
        ),
        pytest.param(
            "layers.composition.create_default_wiki_pipeline_application",
            "app",
            id="composition-module",
        ),
    ],
)
def test_create_default_pipeline_application_wires_components(
    monkeypatch: pytest.MonkeyPatch,
    factory: str,
    expected: str,
    tmp_path: Path,
) -> None:
    module_name = factory.rsplit(".", maxsplit=1)[0]
    function_name = factory.rsplit(".", maxsplit=1)[1]
    module = importlib.import_module(module_name)
    captured: dict[str, object] = {}

    monkeypatch.setattr(
        module,
        "LayerZeroMergeService",
        lambda **kwargs: ("merge", kwargs),
    )
    monkeypatch.setattr(module, "LayerZeroExecutor", lambda **kwargs: ("l0", kwargs))
    monkeypatch.setattr(module, "LayerOneExecutor", lambda **kwargs: ("l1", kwargs))

    def _capture_application(**kwargs):
        captured["kwargs"] = kwargs
        return expected

    monkeypatch.setattr(module, "WikiPipelineApplication", _capture_application)

    result = getattr(module, function_name)(
        base_wiki_dir=tmp_path / "wiki",
        base_debug_dir=tmp_path / "debug",
    )

    assert result == expected
    assert "layer_zero_executor" in captured["kwargs"]
    assert "layer_one_executor" in captured["kwargs"]
    assert "layer_zero_merge_service" in captured["kwargs"]


@pytest.mark.parametrize(
    ("factory_builder", "expected"),
    [
        (
            lambda: importlib.import_module(
                "layers.orchestration.factories",
            ).DefaultLayerZeroRunConfigFactory(),
            {},
        ),
        (
            lambda: importlib.import_module(
                "layers.orchestration.factories",
            ).StaticScraperKwargsFactory(
                scraper_kwargs={"export_scope": "history"},
            ),
            {"export_scope": "history"},
        ),
    ],
)
def test_run_config_factories_return_expected_scraper_kwargs(
    factory_builder,
    expected: dict[str, object],
) -> None:
    factory = factory_builder()

    assert factory.create_scraper_kwargs(job=None) == expected


@pytest.mark.parametrize("missing_key", [True, False])
def test_sponsorship_liveries_factory_fallback_and_success(
    monkeypatch: pytest.MonkeyPatch,
    missing_key: bool,  # noqa: FBT001
) -> None:
    from layers.orchestration import factories
    from layers.seed.registry.entries import ListJobRegistryEntry

    job = ListJobRegistryEntry(
        seed_name="sponsorship_liveries",
        wikipedia_url="https://example.com",
        output_category="teams",
        list_scraper_cls=type("SponsorshipScraper", (), {}),
        json_output_path="x",
        legacy_json_output_path="y",
    )

    monkeypatch.setattr(
        factories,
        "ParenClassifier",
        lambda gemini_client: ("classifier", gemini_client),
    )
    if missing_key:
        monkeypatch.setattr(
            factories.GeminiClient,
            "from_key_file",
            staticmethod(lambda: (_ for _ in ()).throw(FileNotFoundError("missing"))),
        )
    else:
        monkeypatch.setattr(
            factories.GeminiClient,
            "from_key_file",
            staticmethod(lambda: "gemini"),
        )

    kwargs = factories.SponsorshipLiveriesRunConfigFactory().create_scraper_kwargs(job)

    if missing_key:
        assert kwargs == {}
    else:
        assert kwargs == {"classifier": ("classifier", "gemini")}


def test_orchestration_helpers_exports_and_emits_deprecation_warning() -> None:
    sys.modules.pop("layers.orchestration.helpers", None)
    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always")
        helpers = importlib.import_module("layers.orchestration.helpers")

    assert any(item.category is DeprecationWarning for item in recorded)
    assert callable(helpers.build_layer_one_runner_map)
    assert callable(helpers.build_layer_zero_run_config_factory_map)


@pytest.mark.parametrize(
    ("discovered", "explicit", "expected_runner"),
    [
        (
            {"drivers": "d"},
            {"drivers": "e", "seasons": "s"},
            {"drivers": "d", "seasons": "s"},
        ),
        ({}, {"drivers": "e"}, {"drivers": "e"}),
        ({"drivers": "d"}, {}, {"drivers": "d"}),
    ],
)
def test_merge_runner_maps_prefers_discovered_and_falls_back_to_explicit(
    discovered: dict[str, object],
    explicit: dict[str, object],
    expected_runner: dict[str, object],
) -> None:
    from layers.orchestration.runner_registry import _merge_runner_maps

    assert _merge_runner_maps(discovered, explicit) == expected_runner


@pytest.mark.parametrize(
    ("seed_name", "expected_scope"),
    [
        ("constructors_current", "current"),
        ("constructors_former", "former"),
        ("constructors_indianapolis_only", "indianapolis"),
        ("constructors_privateer", "privateer"),
        ("engines_indianapolis_only", "indianapolis_only"),
        ("points_sprint", "sprint"),
        ("points_shortened", "shortened"),
        ("points_history", "history"),
    ],
)
def test_build_layer_zero_factory_map_parametrized(
    seed_name: str,
    expected_scope: str,
) -> None:
    from layers.orchestration.runner_registry import (
        build_layer_zero_run_config_factory_map,
    )

    factory_map = build_layer_zero_run_config_factory_map()

    assert factory_map[seed_name].create_scraper_kwargs(job=None) == {
        "export_scope": expected_scope,
    }


def test_runner_map_missing_runner_and_invalid_key_behaviour(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from layers.orchestration import runner_registry

    monkeypatch.setattr(runner_registry, "build_layer_one_runner_map_discovered", dict)
    monkeypatch.setattr(
        runner_registry,
        "_build_explicit_layer_one_runner_map",
        lambda: {"drivers": object()},
    )

    runner_map = runner_registry.build_layer_one_runner_map()

    assert runner_map.get("unknown_seed") is None
    with pytest.raises(KeyError):
        _ = runner_map["unknown_seed"]
