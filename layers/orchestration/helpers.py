from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING

from layers.orchestration.factories import SponsorshipLiveriesRunConfigFactory
from layers.orchestration.runners.function_export import FunctionExportRunner
from layers.orchestration.runners.grand_prix import GrandPrixRunner
from scrapers.base.architecture_registry import ARCHITECTURE_REGISTRY
from scrapers.engines.helpers.export import export_complete_engine_manufacturers
from scrapers.wiki.discovery import build_layer_one_runner_map_discovered

if TYPE_CHECKING:
    from pathlib import Path

    from layers.orchestration.protocols import LayerOneRunnerProtocol
    from layers.orchestration.protocols import LayerZeroRunConfigFactoryProtocol


def _import_target(path: str) -> object:
    module_name, attr_name = path.split(":", maxsplit=1)
    module = import_module(module_name)
    return getattr(module, attr_name)


def _build_explicit_layer_one_runner_map() -> dict[str, LayerOneRunnerProtocol]:
    runners: dict[str, LayerOneRunnerProtocol] = {}
    for spec in ARCHITECTURE_REGISTRY.layer_one_runners:
        if spec.runner_kind == "grand_prix":
            runners[spec.seed_name] = GrandPrixRunner()
            continue
        if (
            spec.runner_kind == "function_export"
            and spec.export_function_path is not None
        ):
            export_function = _import_target(spec.export_function_path)
            if callable(export_function):
                runners[spec.seed_name] = FunctionExportRunner(
                    export_function=export_function,
                    component_metadata=spec.component_metadata,
                )
                continue
        msg = f"Unsupported runner spec for seed={spec.seed_name}: {spec}"
        raise ValueError(msg)
    return runners


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
