from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING

from layers.orchestration.factories import SponsorshipLiveriesRunConfigFactory
from layers.orchestration.protocols import LayerOneRunnerProtocol
from layers.orchestration.protocols import LayerZeroRunConfigFactoryProtocol
from layers.orchestration.runners.function_export import FunctionExportRunner
from scrapers.engines.helpers.export import export_complete_engine_manufacturers
from scrapers.wiki.discovery import build_layer_one_runner_map_discovered
from tests.architecture.rules import get_layer_one_runner_specs
from tests.architecture.rules import validate_architecture_registry_or_raise

if TYPE_CHECKING:
    from pathlib import Path


def _import_target(path: str) -> object:
    module_name, attr_name = path.split(":", maxsplit=1)
    module = import_module(module_name)
    return getattr(module, attr_name)


def _build_explicit_layer_one_runner_map() -> dict[str, LayerOneRunnerProtocol]:
    validate_architecture_registry_or_raise()
    explicit_map: dict[str, LayerOneRunnerProtocol] = {}
    for spec in get_layer_one_runner_specs():
        if spec.layer_one_runner_path is not None:
            runner_cls = _import_target(spec.layer_one_runner_path)
            explicit_map[spec.domain] = runner_cls()
            continue

        if spec.layer_one_export_function_path is None:
            continue

        export_function = _import_target(spec.layer_one_export_function_path)
        explicit_map[spec.domain] = FunctionExportRunner(
            export_function=export_function,
            component_metadata={
                "domain": spec.domain,
                "seed_name": spec.domain,
                "layer": "layer_one",
                "output_category": spec.domain,
                "component_type": "runner",
            },
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
