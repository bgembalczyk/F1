from __future__ import annotations

import shutil
from datetime import datetime
from datetime import timezone
from typing import TYPE_CHECKING

from layers.constructors_mirror_service import ConstructorsMirrorService
from layers.one.executor import LayerOneExecutor
from layers.orchestration.adapter_registry import get_default_layer_adapter_registry
from layers.orchestration.adapter_registry import validate_layer_adapter_registry
from layers.pipeline import WikiPipelineApplication
from layers.zero.executor import LayerZeroExecutor
from layers.zero.merge import merge_layer_zero_raw_outputs
from layers.zero.merge_service import LayerZeroMergeService

if TYPE_CHECKING:
    from pathlib import Path


def _current_year() -> int:
    return datetime.now(tz=timezone.utc).year


def create_default_wiki_pipeline_application(
    *,
    base_wiki_dir: Path,
    base_debug_dir: Path,
) -> WikiPipelineApplication:
    adapter_registry = get_default_layer_adapter_registry()
    validate_layer_adapter_registry(adapter_registry)

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
        list_job_registry=adapter_registry.layer_zero.list_job_registry,
        validate_list_registry=adapter_registry.layer_zero.validate_list_registry,
        run_config_factory_map_builder=adapter_registry.layer_zero.run_config_factory_map_builder,
        default_config_factory=adapter_registry.layer_zero.default_config_factory,
        run_and_export_function=adapter_registry.layer_zero.run_and_export_function,
        constructors_mirror_service=constructors_mirror_service,
        merge_service=LayerZeroMergeService(
            merge_function=merge_layer_zero_raw_outputs,
        ),
        current_constructors_scraper_name="CurrentConstructorsListScraper",
        year_provider=_current_year,
    )

    layer_one_executor = LayerOneExecutor(
        seed_registry=adapter_registry.layer_one.seed_registry,
        validate_seed_registry_function=adapter_registry.layer_one.validate_seed_registry_function,
        runner_map_builder=adapter_registry.layer_one.runner_map_builder,
        engine_manufacturers_runner=adapter_registry.layer_one.engine_manufacturers_runner,
    )

    return WikiPipelineApplication(
        base_wiki_dir=base_wiki_dir,
        base_debug_dir=base_debug_dir,
        layer_zero_executor=layer_zero_executor,
        layer_one_executor=layer_one_executor,
    )
