from __future__ import annotations

import shutil
from datetime import datetime
from datetime import timezone
from typing import TYPE_CHECKING

from layers.constructors_mirror_service import ConstructorsMirrorService
from layers.one.executor import LayerOneExecutor
from layers.orchestration.factories import DefaultLayerZeroRunConfigFactory
from layers.orchestration.helpers import build_layer_one_runner_map
from layers.orchestration.helpers import build_layer_zero_run_config_factory_map
from layers.orchestration.helpers import run_engine_manufacturers
from layers.pipeline import WikiPipelineApplication
from layers.seed.registry.constants import WIKI_LIST_JOB_REGISTRY
from layers.seed.registry.helpers import get_wiki_seed_registry
from layers.seed.registry.helpers import validate_list_job_registry
from layers.seed.registry.helpers import validate_seed_registry
from layers.zero.executor import LayerZeroExecutor
from layers.zero.merge import merge_layer_zero_raw_outputs
from layers.zero.merge_service import LayerZeroMergeService
from layers.zero.policies import MirrorConstructorsJobHook

if TYPE_CHECKING:
    from pathlib import Path


def _current_year() -> int:
    return datetime.now(tz=timezone.utc).year


def create_default_wiki_pipeline_application(
    *,
    base_wiki_dir: Path,
    base_debug_dir: Path,
) -> WikiPipelineApplication:
    constructors_mirror_service = ConstructorsMirrorService(
        mirror_targets=(
            ("chassis_constructors", "f1_constructors_{year}.json"),
            ("constructors", "f1_constructors_{year}.json"),
            ("teams", "f1_constructors_{year}.json"),
        ),
        copy_file=shutil.copy2,
        year_provider=_current_year,
    )

    layer_zero_executor = LayerZeroExecutor(
        list_job_registry=WIKI_LIST_JOB_REGISTRY,
        validate_list_registry=validate_list_job_registry,
        run_config_factory_map_builder=build_layer_zero_run_config_factory_map,
        default_config_factory=DefaultLayerZeroRunConfigFactory(),
        merge_service=LayerZeroMergeService(
            merge_function=merge_layer_zero_raw_outputs,
        ),
        job_hook=MirrorConstructorsJobHook(
            constructors_mirror_service=constructors_mirror_service,
            should_mirror_predicate=(
                lambda job: job.list_scraper_cls.__name__
                == "CurrentConstructorsListScraper"
            ),
        ),
        year_provider=_current_year,
    )

    layer_one_executor = LayerOneExecutor(
        seed_registry=get_wiki_seed_registry(),
        validate_seed_registry_function=validate_seed_registry,
        runner_map_builder=build_layer_one_runner_map,
        engine_manufacturers_runner=run_engine_manufacturers,
    )

    return WikiPipelineApplication(
        base_wiki_dir=base_wiki_dir,
        base_debug_dir=base_debug_dir,
        layer_zero_executor=layer_zero_executor,
        layer_one_executor=layer_one_executor,
    )
