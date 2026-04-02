from __future__ import annotations

from typing import TYPE_CHECKING

from layers.orchestration.factories import SponsorshipLiveriesRunConfigFactory
from layers.orchestration.factories import StaticScraperKwargsFactory
from layers.orchestration.protocols import LayerOneRunnerProtocol
from layers.orchestration.protocols import LayerZeroRunConfigFactoryProtocol
from layers.orchestration.runners.function_export import FunctionExportRunner
from layers.orchestration.runners.grand_prix import GrandPrixRunner
from layers.orchestration.runners.metadata import build_runner_metadata
from scrapers.circuits.helpers.export import export_complete_circuits
from scrapers.constructors.helpers.export import export_complete_constructors
from scrapers.drivers.helpers.export import export_complete_drivers
from scrapers.engines.helpers.export import export_complete_engine_manufacturers
from scrapers.seasons.helpers import export_complete_seasons
from scrapers.wiki.discovery import build_layer_one_runner_map_discovered

if TYPE_CHECKING:
    from pathlib import Path


def _build_explicit_layer_one_runner_map() -> dict[str, LayerOneRunnerProtocol]:
    return {
        "grands_prix": GrandPrixRunner(),
        "circuits": FunctionExportRunner(
            export=export_complete_circuits,
            component_metadata=build_runner_metadata("circuits"),
        ),
        "drivers": FunctionExportRunner(
            export=export_complete_drivers,
            component_metadata=build_runner_metadata("drivers"),
        ),
        "seasons": FunctionExportRunner(
            export=export_complete_seasons,
            component_metadata=build_runner_metadata("seasons"),
        ),
        "constructors": FunctionExportRunner(
            export=export_complete_constructors,
            component_metadata=build_runner_metadata("constructors"),
        ),
    }


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
        "constructors_current": StaticScraperKwargsFactory(
            scraper_kwargs={"export_scope": "current"},
        ),
        "constructors_former": StaticScraperKwargsFactory(
            scraper_kwargs={"export_scope": "former"},
        ),
        "constructors_indianapolis_only": StaticScraperKwargsFactory(
            scraper_kwargs={"export_scope": "indianapolis"},
        ),
        "constructors_privateer": StaticScraperKwargsFactory(
            scraper_kwargs={"export_scope": "privateer"},
        ),
        "engines_indianapolis_only": StaticScraperKwargsFactory(
            scraper_kwargs={"export_scope": "indianapolis_only"},
        ),
        "points_sprint": StaticScraperKwargsFactory(
            scraper_kwargs={"export_scope": "sprint"},
        ),
        "points_shortened": StaticScraperKwargsFactory(
            scraper_kwargs={"export_scope": "shortened"},
        ),
        "points_history": StaticScraperKwargsFactory(
            scraper_kwargs={"export_scope": "history"},
        ),
        "grands_prix_red_flagged_world_championship": StaticScraperKwargsFactory(
            scraper_kwargs={"export_scope": "world_championship"},
        ),
        "grands_prix_red_flagged_non_championship": StaticScraperKwargsFactory(
            scraper_kwargs={"export_scope": "non_championship"},
        ),
        "sponsorship_liveries": SponsorshipLiveriesRunConfigFactory(),
    }


def run_engine_manufacturers(*, base_wiki_dir: Path, include_urls: bool) -> None:
    print("[complete] running  F1CompleteEngineManufacturerDataExtractor")
    export_complete_engine_manufacturers(
        output_dir=base_wiki_dir / "engines/complete_engine_manufacturers",
        include_urls=include_urls,
    )
    print("[complete] finished F1CompleteEngineManufacturerDataExtractor")
