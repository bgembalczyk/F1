from __future__ import annotations

from typing import TYPE_CHECKING

from layers.orchestration.factories import SponsorshipLiveriesRunConfigFactory
from layers.orchestration.factories import StaticScraperKwargsFactory
from layers.orchestration.protocols import LayerOneRunnerProtocol
from layers.orchestration.protocols import LayerZeroRunConfigFactoryProtocol
from layers.orchestration.runners.function_export import FunctionExportRunner
from layers.orchestration.runners.grand_prix import GrandPrixRunner
from layers.orchestration.runners.metadata import build_runner_metadata
from layers.seed.registry.types import SeedName
from layers.seed.registry.types import parse_seed_name
from scrapers.circuits.helpers.export import export_complete_circuits
from scrapers.constructors.helpers.export import export_complete_constructors
from scrapers.drivers.helpers.export import export_complete_drivers
from scrapers.engines.helpers.export import export_complete_engine_manufacturers
from scrapers.seasons.helpers import export_complete_seasons
from scrapers.wiki.discovery import build_layer_one_runner_map_discovered

if TYPE_CHECKING:
    from pathlib import Path


def _build_explicit_layer_one_runner_map() -> dict[SeedName, LayerOneRunnerProtocol]:
    return {
        SeedName.GRANDS_PRIX: GrandPrixRunner(),
        SeedName.CIRCUITS: FunctionExportRunner(
            export_function=export_complete_circuits,
            component_metadata=build_runner_metadata("circuits"),
        ),
        SeedName.DRIVERS: FunctionExportRunner(
            export_function=export_complete_drivers,
            component_metadata=build_runner_metadata("drivers"),
        ),
        SeedName.SEASONS: FunctionExportRunner(
            export_function=export_complete_seasons,
            component_metadata=build_runner_metadata("seasons"),
        ),
        SeedName.CONSTRUCTORS: FunctionExportRunner(
            export_function=export_complete_constructors,
            component_metadata=build_runner_metadata("constructors"),
        ),
    }


def _merge_runner_maps(
    discovered: dict[SeedName, LayerOneRunnerProtocol],
    explicit: dict[SeedName, LayerOneRunnerProtocol],
) -> dict[SeedName, LayerOneRunnerProtocol]:
    merged = dict(discovered)
    for seed_name, runner in explicit.items():
        merged.setdefault(seed_name, runner)
    return merged


def build_layer_one_runner_map() -> dict[SeedName, LayerOneRunnerProtocol]:
    explicit_runner_map = _build_explicit_layer_one_runner_map()
    discovered_runner_map = {
        parse_seed_name(seed_name): runner
        for seed_name, runner in build_layer_one_runner_map_discovered().items()
    }
    return _merge_runner_maps(discovered_runner_map, explicit_runner_map)


def build_layer_zero_run_config_factory_map() -> dict[
    SeedName,
    LayerZeroRunConfigFactoryProtocol,
]:
    return {
        SeedName.CONSTRUCTORS_CURRENT: StaticScraperKwargsFactory(
            scraper_kwargs={"export_scope": "current"},
        ),
        SeedName.CONSTRUCTORS_FORMER: StaticScraperKwargsFactory(
            scraper_kwargs={"export_scope": "former"},
        ),
        SeedName.CONSTRUCTORS_INDIANAPOLIS_ONLY: StaticScraperKwargsFactory(
            scraper_kwargs={"export_scope": "indianapolis"},
        ),
        SeedName.CONSTRUCTORS_PRIVATEER: StaticScraperKwargsFactory(
            scraper_kwargs={"export_scope": "privateer"},
        ),
        SeedName.ENGINES_INDIANAPOLIS_ONLY: StaticScraperKwargsFactory(
            scraper_kwargs={"export_scope": "indianapolis_only"},
        ),
        SeedName.POINTS_SPRINT: StaticScraperKwargsFactory(
            scraper_kwargs={"export_scope": "sprint"},
        ),
        SeedName.POINTS_SHORTENED: StaticScraperKwargsFactory(
            scraper_kwargs={"export_scope": "shortened"},
        ),
        SeedName.POINTS_HISTORY: StaticScraperKwargsFactory(
            scraper_kwargs={"export_scope": "history"},
        ),
        SeedName.GRANDS_PRIX_RED_FLAGGED_WORLD_CHAMPIONSHIP: StaticScraperKwargsFactory(
            scraper_kwargs={"export_scope": "world_championship"},
        ),
        SeedName.GRANDS_PRIX_RED_FLAGGED_NON_CHAMPIONSHIP: StaticScraperKwargsFactory(
            scraper_kwargs={"export_scope": "non_championship"},
        ),
        SeedName.SPONSORSHIP_LIVERIES: SponsorshipLiveriesRunConfigFactory(),
    }


def run_engine_manufacturers(*, base_wiki_dir: Path, include_urls: bool) -> None:
    print("[complete] running  F1CompleteEngineManufacturerDataExtractor")
    export_complete_engine_manufacturers(
        output_dir=base_wiki_dir / "engines/complete_engine_manufacturers",
        include_urls=include_urls,
    )
    print("[complete] finished F1CompleteEngineManufacturerDataExtractor")
