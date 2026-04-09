from __future__ import annotations

import shutil
from datetime import datetime
from datetime import timezone
from typing import TYPE_CHECKING
from typing import NamedTuple

from layers.constructors_mirror_service import ConstructorsMirrorService
from layers.orchestration.runner_registry import build_layer_one_runner_map
from layers.orchestration.runner_registry import build_layer_zero_run_config_factory_map
from layers.orchestration.runner_registry import run_engine_manufacturers
from layers.seed.registry.constants import WIKI_LIST_JOB_REGISTRY
from layers.seed.registry.helpers import get_wiki_seed_registry
from layers.seed.registry.helpers import validate_list_job_registry
from layers.seed.registry.helpers import validate_seed_registry
from layers.zero.d_merge import merge_layer_zero_phase_d
from layers.zero.extract import extract_layer_zero_phase_c
from layers.zero.merge import merge_layer_zero_raw_outputs
from layers.zero.merge_service import LayerZeroMergeService
from wiki_pipeline.components.factory import WikiPipelineComponentsFactory
from wiki_pipeline.applications import WikiPipelineApplication

if TYPE_CHECKING:
    from pathlib import Path






def create_default_wiki_pipeline_application(
    *,
    base_wiki_dir: Path,
    base_debug_dir: Path,
) -> WikiPipelineApplication:
    """Composition root dla domyślnej aplikacji wiki pipeline."""
    components = WikiPipelineComponentsFactory.build_components()
    return WikiPipelineApplication(
        base_wiki_dir=base_wiki_dir,
        base_debug_dir=base_debug_dir,
        layer_zero_executor=components.layer_zero_executor,
        layer_one_executor=components.layer_one_executor,
        layer_zero_merge_service=components.layer_zero_merge_service,
    )
