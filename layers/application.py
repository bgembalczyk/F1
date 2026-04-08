"""Backward-compatible module alias for the canonical composition root."""

from pathlib import Path

from layers.composition import WikiPipelineComponentsFactory
from layers.composition import create_default_wiki_pipeline_application
from layers.facade import WikiPipelineFacade
from layers.pipeline import WikiPipelineApplication
from layers.seed.registry.constants import WIKI_LIST_JOB_REGISTRY
from layers.seed.registry.helpers import get_wiki_seed_registry
from layers.seed.registry.helpers import validate_list_job_registry
from layers.seed.registry.helpers import validate_seed_registry
from layers.zero.d_merge import merge_layer_zero_phase_d
from layers.zero.executor import LayerZeroExecutor
from layers.zero.extract import extract_layer_zero_phase_c
from layers.zero.merge import merge_layer_zero_raw_outputs
from layers.zero.merge_service import LayerZeroMergeService
from layers.zero.policies import CompositeLayerZeroJobHook
from layers.zero.policies import MirrorConstructorsJobHook
from layers.zero.policies import MirrorToDomainByFilenameJobHook
from layers.zero.run_profile_paths import build_debug_run_config

__all__ = [
    "create_default_wiki_pipeline_application",
    "create_default_wiki_pipeline_facade",
]


def create_default_wiki_pipeline_facade(
    *,
    base_wiki_dir: Path,
    base_debug_dir: Path,
) -> WikiPipelineFacade:
    components = WikiPipelineComponentsFactory.build_components()
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


