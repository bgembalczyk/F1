"""Backward-compatible module alias for the canonical composition root."""

from pathlib import Path

from layers.zero.run_profile_paths import build_debug_run_config
from wiki_pipeline.components.factory import WikiPipelineComponentsFactory
from wiki_pipeline.facade import WikiPipelineFacade


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
