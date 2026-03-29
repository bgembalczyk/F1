from __future__ import annotations

from typing import TYPE_CHECKING

from layers.orchestration.factories import SponsorshipLiveriesRunConfigFactory
from layers.orchestration.protocols import LayerOneRunnerProtocol
from layers.orchestration.protocols import LayerZeroRunConfigFactoryProtocol
from layers.types import DomainName
from layers.orchestration.runners.circuits import CircuitsRunner
from layers.orchestration.runners.constructors import ConstructorsRunner
from layers.orchestration.runners.drivers import DriversRunner
from layers.orchestration.runners.function_export import FunctionExportRunner
from layers.orchestration.runners.grand_prix import GrandPrixRunner
from scrapers.circuits.helpers.export import export_complete_circuits
from scrapers.constructors.helpers.export import export_complete_constructors
from scrapers.drivers.helpers.export import export_complete_drivers
from scrapers.engines.helpers.export import export_complete_engine_manufacturers
from scrapers.seasons.helpers import export_complete_seasons
from scrapers.wiki.discovery import build_layer_one_runner_map_discovered

if TYPE_CHECKING:
    from pathlib import Path


def _build_explicit_layer_one_runner_map() -> dict[DomainName, LayerOneRunnerProtocol]:
    return {
        DomainName.GRANDS_PRIX: GrandPrixRunner(),
        DomainName.CIRCUITS: FunctionExportRunner(
            export_function=export_complete_circuits,
            component_metadata={
                "domain": "circuits",
                "seed_name": "circuits",
                "layer": "layer_one",
                "output_category": "circuits",
                "component_type": "runner",
            },
        ),
        DomainName.DRIVERS: FunctionExportRunner(
            export_function=export_complete_drivers,
            component_metadata={
                "domain": "drivers",
                "seed_name": "drivers",
                "layer": "layer_one",
                "output_category": "drivers",
                "component_type": "runner",
            },
        ),
        DomainName.SEASONS: FunctionExportRunner(
            export_function=export_complete_seasons,
            component_metadata={
                "domain": "seasons",
                "seed_name": "seasons",
                "layer": "layer_one",
                "output_category": "seasons",
                "component_type": "runner",
            },
        ),
        DomainName.CONSTRUCTORS: FunctionExportRunner(
            export_function=export_complete_constructors,
            component_metadata={
                "domain": "constructors",
                "seed_name": "constructors",
                "layer": "layer_one",
                "output_category": "constructors",
                "component_type": "runner",
            },
        ),
    }


def _merge_runner_maps(
    discovered: dict[str, LayerOneRunnerProtocol],
    explicit: dict[DomainName, LayerOneRunnerProtocol],
) -> dict[DomainName, LayerOneRunnerProtocol]:
    merged: dict[DomainName, LayerOneRunnerProtocol] = {
        DomainName.from_io(seed_name): runner for seed_name, runner in discovered.items()
    }
    for domain, runner in explicit.items():
        merged.setdefault(domain, runner)
    return merged


def build_layer_one_runner_map() -> dict[DomainName, LayerOneRunnerProtocol]:
    explicit_runner_map = _build_explicit_layer_one_runner_map()
    discovered_runner_map = build_layer_one_runner_map_discovered()
    return _merge_runner_maps(discovered_runner_map, explicit_runner_map)


def build_layer_zero_run_config_factory_map() -> dict[
    DomainName,
    LayerZeroRunConfigFactoryProtocol,
]:
    return {
        DomainName.SPONSORSHIP_LIVERIES: SponsorshipLiveriesRunConfigFactory(),
    }


def run_engine_manufacturers(*, base_wiki_dir: Path, include_urls: bool) -> None:
    print("[complete] running  F1CompleteEngineManufacturerDataExtractor")
    export_complete_engine_manufacturers(
        output_dir=base_wiki_dir / "engines/complete_engine_manufacturers",
        include_urls=include_urls,
    )
    print("[complete] finished F1CompleteEngineManufacturerDataExtractor")
