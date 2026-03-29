from __future__ import annotations

import shutil
from datetime import datetime
from datetime import timezone
from functools import partial
from typing import TYPE_CHECKING

from layers.constructors_mirror_service import ConstructorsMirrorService
from layers.one.executor import LayerOneExecutor
from layers.orchestration.factories import DefaultLayerZeroRunConfigFactory
from layers.orchestration.helpers import build_layer_one_runner_map
from layers.orchestration.helpers import build_layer_zero_run_config_factory_map
from layers.orchestration.helpers import run_engine_manufacturers
from layers.orchestration.progress_reporter import StdoutProgressReporter
from layers.pipeline import WikiPipelineApplication
from layers.seed.registry.constants import WIKI_LIST_JOB_REGISTRY
from layers.seed.registry.helpers import WIKI_SEED_REGISTRY
from layers.seed.registry.helpers import validate_list_job_registry
from layers.seed.registry.helpers import validate_seed_registry
from layers.zero.executor import LayerZeroExecutor
from layers.zero.merge import merge_layer_zero_raw_outputs
from layers.zero.merge_service import LayerZeroMergeService
from scrapers.base.helpers.runner import run_and_export

if TYPE_CHECKING:
    from pathlib import Path


def _current_year() -> int:
    return datetime.now(tz=timezone.utc).year


def create_default_wiki_pipeline_application(
    *,
    base_wiki_dir: Path,
    base_debug_dir: Path,
) -> WikiPipelineApplication:
    progress_reporter = StdoutProgressReporter()

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
        run_config_factory_map_builder=partial(
            build_layer_zero_run_config_factory_map,
            progress_reporter,
        ),
        default_config_factory=DefaultLayerZeroRunConfigFactory(),
        run_and_export_function=run_and_export,
        constructors_mirror_service=constructors_mirror_service,
        merge_service=LayerZeroMergeService(
            merge_function=merge_layer_zero_raw_outputs,
        ),
        current_constructors_scraper_name="CurrentConstructorsListScraper",
        year_provider=_current_year,
        progress_reporter=progress_reporter,
    )

    layer_one_executor = LayerOneExecutor(
        seed_registry=WIKI_SEED_REGISTRY,
        validate_seed_registry_function=validate_seed_registry,
        runner_map_builder=build_layer_one_runner_map,
        engine_manufacturers_runner=partial(
            run_engine_manufacturers,
            progress_reporter=progress_reporter,
        ),
        progress_reporter=progress_reporter,
    )

    return WikiPipelineApplication(
        base_wiki_dir=base_wiki_dir,
        base_debug_dir=base_debug_dir,
        layer_zero_executor=layer_zero_executor,
        layer_one_executor=layer_one_executor,
    )
