"""Backward-compatible module alias for the canonical composition root."""

import shutil
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import NamedTuple

from layers.composition import create_default_wiki_pipeline_application
from layers.constructors_mirror_service import ConstructorsMirrorService
from layers.facade import WikiPipelineFacade
from layers.one.executor import LayerOneExecutor
from layers.orchestration.factories import DefaultLayerZeroRunConfigFactory
from layers.orchestration.runner_registry import build_layer_one_runner_map
from layers.orchestration.runner_registry import build_layer_zero_run_config_factory_map
from layers.orchestration.runner_registry import run_engine_manufacturers
from layers.pipeline import WikiPipelineApplication
from layers.seed.registry import WIKI_LIST_JOB_REGISTRY
from layers.seed.registry import get_wiki_seed_registry
from layers.seed.registry import validate_list_job_registry
from layers.seed.registry import validate_seed_registry
from layers.zero.executor import LayerZeroExecutor
from layers.zero.merge import merge_layer_zero_raw_outputs
from layers.zero.merge_service import LayerZeroMergeService
from layers.zero.policies import MirrorConstructorsJobHook
from layers.zero.run_profile_paths import build_debug_run_config


class _WikiPipelineComponents(NamedTuple):
    layer_zero_executor: LayerZeroExecutor
    layer_one_executor: LayerOneExecutor
    layer_zero_merge_service: LayerZeroMergeService


def _current_year() -> int:
    return datetime.now(tz=timezone.utc).year


def _should_mirror_constructors_job(job: object) -> bool:
    """Aktywna dla `CurrentConstructorsListScraper` i `ConstructorsListScraper`."""
    list_scraper_cls = getattr(job, "list_scraper_cls", None)
    scraper_name = getattr(list_scraper_cls, "__name__", "")
    return scraper_name in {"CurrentConstructorsListScraper", "ConstructorsListScraper"}


def _build_default_wiki_pipeline_components() -> _WikiPipelineComponents:
    layer_zero_merge_service = LayerZeroMergeService(
        merge=merge_layer_zero_raw_outputs,
    )

    layer_zero_executor = LayerZeroExecutor(
        list_job_registry=WIKI_LIST_JOB_REGISTRY,
        validate_list_registry=validate_list_job_registry,
        config_factories=build_layer_zero_run_config_factory_map,
        default_config_factory=DefaultLayerZeroRunConfigFactory(),
        merger=layer_zero_merge_service,
        job_hook=MirrorConstructorsJobHook(
            mirror=ConstructorsMirrorService(
                mirror_targets=(
                    ("chassis_constructors", "f1_constructors_{year}.json"),
                    ("constructors", "f1_constructors_{year}.json"),
                    ("teams", "f1_constructors_{year}.json"),
                ),
                copy_file=shutil.copy2,
                year_provider=_current_year,
            ),
            should_mirror_predicate=_should_mirror_constructors_job,
        ),
        year_provider=_current_year,
    )

    layer_one_executor = LayerOneExecutor(
        seed_registry=get_wiki_seed_registry(),
        validate_seed_registry=validate_seed_registry,
        runners=build_layer_one_runner_map,
        engine_manufacturers_runner=run_engine_manufacturers,
    )

    return _WikiPipelineComponents(
        layer_zero_executor=layer_zero_executor,
        layer_one_executor=layer_one_executor,
        layer_zero_merge_service=layer_zero_merge_service,
    )


def create_default_wiki_pipeline_facade(
    *,
    base_wiki_dir: Path,
    base_debug_dir: Path,
) -> WikiPipelineFacade:
    components = _build_default_wiki_pipeline_components()
    return WikiPipelineFacade(
        base_wiki_dir=base_wiki_dir,
        base_debug_dir=base_debug_dir,
        layer_zero_executor=components.layer_zero_executor,
        layer_one_executor=components.layer_one_executor,
        layer_zero_merge_service=components.layer_zero_merge_service,
        run_config_factory=lambda: build_debug_run_config(
            base_wiki_dir=base_wiki_dir,
            base_debug_dir=base_debug_dir,
        ),
    )


def create_default_wiki_pipeline_application(
    *,
    base_wiki_dir: Path,
    base_debug_dir: Path,
) -> WikiPipelineApplication:
    components = _build_default_wiki_pipeline_components()

    return WikiPipelineApplication(
        base_wiki_dir=base_wiki_dir,
        base_debug_dir=base_debug_dir,
        layer_zero_executor=components.layer_zero_executor,
        layer_one_executor=components.layer_one_executor,
        layer_zero_merge_service=components.layer_zero_merge_service,
    )
