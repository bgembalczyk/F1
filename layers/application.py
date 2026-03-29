from __future__ import annotations

import shutil
from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Callable

from layers.constructors_mirror_service import ConstructorsMirrorService
from layers.one.executor import LayerOneExecutor
from layers.orchestration.factories import DefaultLayerZeroRunConfigFactory
from layers.orchestration.helpers import build_layer_one_runner_map
from layers.orchestration.helpers import build_layer_zero_run_config_factory_map
from layers.orchestration.helpers import run_engine_manufacturers
from layers.pipeline import WikiPipelineApplication
from layers.seed.registry.constants import WIKI_LIST_JOB_REGISTRY
from layers.seed.registry.helpers import WIKI_SEED_REGISTRY
from layers.seed.registry.helpers import validate_list_job_registry
from layers.seed.registry.helpers import validate_seed_registry
from layers.seed.registry.entries import ListJobRegistryEntry
from layers.seed.registry.entries import SeedRegistryEntry
from layers.zero.executor import LayerZeroExecutor
from layers.zero.merge import merge_layer_zero_raw_outputs
from layers.zero.merge_service import LayerZeroMergeService
from scrapers.base.helpers.runner import run_and_export


def _current_year() -> int:
    return datetime.now(tz=timezone.utc).year


def _is_current_constructors_job(job: ListJobRegistryEntry) -> bool:
    return job.seed_name == "constructors_current"


@dataclass(frozen=True)
class PipelineWiringConfig:
    list_job_registry: tuple[ListJobRegistryEntry, ...]
    validate_list_registry: Callable[[tuple[ListJobRegistryEntry, ...]], None]
    run_config_factory_map_builder: Callable[[], dict[str, object]]
    default_config_factory: object
    run_and_export_function: Callable[..., None]
    constructors_mirror_targets: tuple[tuple[str, str], ...]
    constructors_mirror_policy: Callable[[ListJobRegistryEntry], bool]
    merge_function: Callable[[Path], None]
    seed_registry: tuple[SeedRegistryEntry, ...]
    validate_seed_registry_function: Callable[[tuple[SeedRegistryEntry, ...]], None]
    layer_one_runner_map_builder: Callable[[], dict[str, object]]
    engine_manufacturers_runner: Callable[[Path, bool], None]
    year_provider: Callable[[], int]


@dataclass(frozen=True)
class PipelineWiringProfile:
    layer_zero: PipelineWiringConfig
    layer_one: PipelineWiringConfig


def _build_base_wiring_config() -> PipelineWiringConfig:
    return PipelineWiringConfig(
        list_job_registry=WIKI_LIST_JOB_REGISTRY,
        validate_list_registry=validate_list_job_registry,
        run_config_factory_map_builder=build_layer_zero_run_config_factory_map,
        default_config_factory=DefaultLayerZeroRunConfigFactory(),
        run_and_export_function=run_and_export,
        constructors_mirror_targets=(
            ("chassis_constructors", "f1_constructors_{year}.json"),
            ("constructors", "f1_constructors_{year}.json"),
            ("teams", "f1_constructors_{year}.json"),
        ),
        constructors_mirror_policy=_is_current_constructors_job,
        merge_function=merge_layer_zero_raw_outputs,
        seed_registry=WIKI_SEED_REGISTRY,
        validate_seed_registry_function=validate_seed_registry,
        layer_one_runner_map_builder=build_layer_one_runner_map,
        engine_manufacturers_runner=run_engine_manufacturers,
        year_provider=_current_year,
    )


def build_wiring_profile(profile: str = "dev") -> PipelineWiringProfile:
    if profile not in {"dev", "test", "prod"}:
        msg = f"Unsupported wiring profile: {profile}"
        raise ValueError(msg)

    base = _build_base_wiring_config()
    return PipelineWiringProfile(layer_zero=base, layer_one=base)


def build_layer_zero_executor(config: PipelineWiringConfig) -> LayerZeroExecutor:
    constructors_mirror_service = ConstructorsMirrorService(
        mirror_targets=config.constructors_mirror_targets,
        copy_file=shutil.copy2,
        year_provider=config.year_provider,
    )

    return LayerZeroExecutor(
        list_job_registry=config.list_job_registry,
        validate_list_registry=config.validate_list_registry,
        run_config_factory_map_builder=config.run_config_factory_map_builder,
        default_config_factory=config.default_config_factory,
        run_and_export_function=config.run_and_export_function,
        constructors_mirror_service=constructors_mirror_service,
        merge_service=LayerZeroMergeService(
            merge_function=config.merge_function,
        ),
        should_mirror_constructors_job=config.constructors_mirror_policy,
        year_provider=config.year_provider,
    )


def build_layer_one_executor(config: PipelineWiringConfig) -> LayerOneExecutor:
    return LayerOneExecutor(
        seed_registry=config.seed_registry,
        validate_seed_registry_function=config.validate_seed_registry_function,
        runner_map_builder=config.layer_one_runner_map_builder,
        engine_manufacturers_runner=config.engine_manufacturers_runner,
    )


def create_default_wiki_pipeline_application(
    *,
    base_wiki_dir: Path,
    base_debug_dir: Path,
    wiring_profile: str = "dev",
) -> WikiPipelineApplication:
    wiring = build_wiring_profile(wiring_profile)
    layer_zero_executor = build_layer_zero_executor(wiring.layer_zero)
    layer_one_executor = build_layer_one_executor(wiring.layer_one)

    return WikiPipelineApplication(
        base_wiki_dir=base_wiki_dir,
        base_debug_dir=base_debug_dir,
        layer_zero_executor=layer_zero_executor,
        layer_one_executor=layer_one_executor,
    )
