from __future__ import annotations

from typing import TYPE_CHECKING

from layers.orchestration.factories import LayerZeroRunConfigFactory
from layers.orchestration.factories import SponsorshipLiveriesRunConfigFactory
from layers.orchestration.progress_reporter import ProgressReporter
from layers.orchestration.runners.circuits import CircuitsRunner
from layers.orchestration.runners.constructors import ConstructorsRunner
from layers.orchestration.runners.drivers import DriversRunner
from layers.orchestration.runners.grand_prix import GrandPrixRunner
from layers.orchestration.runners.seasons import SeasonsRunner
from scrapers.engines.helpers.export import export_complete_engine_manufacturers
from scrapers.wiki.discovery import build_layer_one_runner_map_discovered

if TYPE_CHECKING:
    from pathlib import Path

    from layers.orchestration.runners.layer_job import LayerJobRunner


def _build_explicit_layer_one_runner_map() -> dict[str, LayerJobRunner]:
    return {
        "grands_prix": GrandPrixRunner(),
        "circuits": CircuitsRunner(),
        "drivers": DriversRunner(),
        "seasons": SeasonsRunner(),
        "constructors": ConstructorsRunner(),
    }


def _merge_runner_maps(
    discovered: dict[str, LayerJobRunner],
    explicit: dict[str, LayerJobRunner],
) -> dict[str, LayerJobRunner]:
    merged = dict(discovered)
    for seed_name, runner in explicit.items():
        merged.setdefault(seed_name, runner)
    return merged


def build_layer_one_runner_map() -> dict[str, LayerJobRunner]:
    explicit_runner_map = _build_explicit_layer_one_runner_map()
    discovered_runner_map = build_layer_one_runner_map_discovered()
    return _merge_runner_maps(discovered_runner_map, explicit_runner_map)


def build_layer_zero_run_config_factory_map() -> dict[str, LayerZeroRunConfigFactory]:
    return {
        "sponsorship_liveries": SponsorshipLiveriesRunConfigFactory(),
    }


def run_engine_manufacturers(
    *,
    base_wiki_dir: Path,
    include_urls: bool,
    progress_reporter: ProgressReporter,
) -> None:
    extractor_name = "F1CompleteEngineManufacturerDataExtractor"
    progress_reporter.job_started("complete", extractor_name)
    export_complete_engine_manufacturers(
        output_dir=base_wiki_dir / "engines/complete_engine_manufacturers",
        include_urls=include_urls,
    )
    progress_reporter.job_finished("complete", extractor_name)
