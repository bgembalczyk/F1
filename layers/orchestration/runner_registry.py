from __future__ import annotations

from typing import TYPE_CHECKING

from layers.orchestration.runtime_factory import RuntimeComponentFactory
from layers.protocols.one_runner import LayerOneRunnerProtocol
from layers.runners.layer_job.function_export import FunctionExportRunner
from layers.runners.metadata import build_runner_metadata
from layers.zero.run_config_factories.protocol import LayerZeroRunConfigFactoryProtocol
from layers.zero.run_config_factories.sponsorship_liveries import SponsorshipLiveriesRunConfigFactory
from layers.zero.run_config_factories.static_scraper_kwargs import StaticScraperKwargsFactory
from scrapers.core.logging import build_execution_context
from scrapers.core.logging import get_logger
from scrapers.domain.exports import export_complete_circuits
from scrapers.domain.exports import export_complete_constructors
from scrapers.domain.exports import export_complete_drivers
from scrapers.domain.exports import export_complete_engine_manufacturers
from scrapers.domain.exports import export_complete_seasons

if TYPE_CHECKING:
    from pathlib import Path

    from layers.orchestration.constants import SeedName

LOGGER = get_logger("RunnerRegistry")


def _build_runtime_factory() -> RuntimeComponentFactory:
    factory = RuntimeComponentFactory()
    factory.discover_and_register(
        root=repo_root(),
        module_globs=(
            "layers/runners/layer_job/*.py",
            "layers/zero/run_config_factories/*.py",
        ),
    )
    return factory


def repo_root() -> Path:
    from pathlib import Path

    return Path(__file__).resolve().parents[2]


def build_explicit_layer_one_runner_map() -> dict[SeedName, LayerOneRunnerProtocol]:
    return {
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


def _build_explicit_layer_one_runner_map() -> dict[SeedName, LayerOneRunnerProtocol]:
    return build_explicit_layer_one_runner_map()


def build_layer_one_runner_map_discovered() -> dict[SeedName, LayerOneRunnerProtocol]:
    factory = _build_runtime_factory()
    return {
        "grands_prix": factory.build(
            role="runner",
            domain="grands_prix",
            stage="layer_one",
        ),
    }


def build_layer_one_runner_map() -> dict[SeedName, LayerOneRunnerProtocol]:
    return merge_runner_maps(
        build_layer_one_runner_map_discovered(),
        _build_explicit_layer_one_runner_map(),
    )


def merge_runner_maps(
    discovered: dict[SeedName, LayerOneRunnerProtocol],
    explicit: dict[SeedName, LayerOneRunnerProtocol],
) -> dict[SeedName, LayerOneRunnerProtocol]:
    merged: dict[SeedName, LayerOneRunnerProtocol] = dict(discovered)
    for seed_name, runner in explicit.items():
        merged.setdefault(seed_name, runner)
    return merged


def build_layer_zero_run_config_factory_map() -> (
    dict[
        SeedName,
        LayerZeroRunConfigFactoryProtocol,
    ]
):
    factory = _build_runtime_factory()
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
        "sponsorship_liveries": factory.build(
            role="run_config_factory",
            domain="sponsorship_liveries",
            stage="layer_zero",
        ),
    }


def run_engine_manufacturers(
    *,
    base_wiki_dir: Path,
    include_urls: bool,
    run_id: str | None = None,
) -> None:
    start_context = build_execution_context(
        run_id=run_id,
        seed_name="engine_manufacturers",
        domain="engines",
        source_name="F1CompleteEngineManufacturerDataExtractor",
        step="export",
        status="started",
    )
    LOGGER.info(
        "[complete] running F1CompleteEngineManufacturerDataExtractor",
        extra=start_context,
    )
    export_complete_engine_manufacturers(
        output_dir=base_wiki_dir / "engines/complete_engine_manufacturers",
        include_urls=include_urls,
    )
    LOGGER.info(
        "[complete] finished F1CompleteEngineManufacturerDataExtractor",
        extra=start_context | {"status": "success"},
    )
