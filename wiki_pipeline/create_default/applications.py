from __future__ import annotations

from typing import TYPE_CHECKING

from wiki_pipeline.applications import WikiPipelineApplication
from wiki_pipeline.components.factory import WikiPipelineComponentsFactory

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
