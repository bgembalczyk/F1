from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, cast

from layers.orchestration.factories import SponsorshipLiveriesRunConfigFactory
from layers.orchestration.protocols import LayerOneRunnerProtocol
from layers.orchestration.protocols import LayerZeroRunConfigFactoryProtocol
from layers.orchestration.runners.function_export import FunctionExportRunner
from scrapers.base.domain_registry import DOMAIN_REGISTRY
from scrapers.base.domain_registry import import_target
from scrapers.engines.helpers.export import export_complete_engine_manufacturers
from scrapers.wiki.discovery import build_layer_one_runner_map_discovered

if TYPE_CHECKING:
    from pathlib import Path


def _build_explicit_layer_one_runner_map() -> dict[str, LayerOneRunnerProtocol]:
    explicit_map: dict[str, LayerOneRunnerProtocol] = {}
    for domain in ("drivers", "constructors", "circuits", "seasons", "grands_prix"):
        runner_meta = DOMAIN_REGISTRY[domain].runner
        if runner_meta.kind == "class":
            runner_cls = cast(type[LayerOneRunnerProtocol], import_target(runner_meta.target_path))
            explicit_map[domain] = runner_cls()
            continue

        export_fn = cast(Callable[..., Any], import_target(runner_meta.target_path))
        explicit_map[domain] = FunctionExportRunner(
            export_function=export_fn,
            component_metadata=runner_meta.component_metadata or {},
        )
    return explicit_map


def _merge_runner_maps(
    discovered: dict[str, LayerOneRunnerProtocol],
    explicit: dict[str, LayerOneRunnerProtocol],
) -> dict[str, LayerOneRunnerProtocol]:
    merged = dict(discovered)
    for seed_name, runner in explicit.items():
        merged.setdefault(seed_name, runner)
    return merged


def build_layer_one_runner_map() -> dict[str, LayerOneRunnerProtocol]:
    explicit_runner_map = _build_explicit_layer_one_runner_map()
    discovered_runner_map = build_layer_one_runner_map_discovered()
    return _merge_runner_maps(discovered_runner_map, explicit_runner_map)


def build_layer_zero_run_config_factory_map() -> dict[
    str,
    LayerZeroRunConfigFactoryProtocol,
]:
    return {
        "sponsorship_liveries": SponsorshipLiveriesRunConfigFactory(),
    }


def run_engine_manufacturers(*, base_wiki_dir: Path, include_urls: bool) -> None:
    print("[complete] running  F1CompleteEngineManufacturerDataExtractor")
    export_complete_engine_manufacturers(
        output_dir=base_wiki_dir / "engines/complete_engine_manufacturers",
        include_urls=include_urls,
    )
    print("[complete] finished F1CompleteEngineManufacturerDataExtractor")
