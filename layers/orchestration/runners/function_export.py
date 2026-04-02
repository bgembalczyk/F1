from __future__ import annotations

from typing import Callable

from layers.orchestration.runners.layer_job import LayerJobRunner
from layers.orchestration.runners.metadata import RunnerMetadata
from layers.orchestration.runtime_config import RuntimeConfig
from layers.seed.registry.entries import SeedRegistryEntry

ExportCallable = Callable[..., None]


class FunctionExportRunner(LayerJobRunner):
    def __init__(
        self,
        *,
        export_function: ExportCallable,
        component_metadata: RunnerMetadata,
    ) -> None:
        self._export_function = export_function
        self.COMPONENT_METADATA = component_metadata

    def run(
        self,
        seed: SeedRegistryEntry,
        runtime_config: RuntimeConfig,
    ) -> None:
        self._export_function(
            output_dir=runtime_config.base_wiki_dir / seed.default_output_path,
            include_urls=runtime_config.include_urls,
        )
