from __future__ import annotations

from pathlib import Path
from typing import Callable

from layers.orchestration.runners.layer_job import LayerJobRunner
from layers.orchestration.runners.metadata import RunnerMetadata
from layers.seed.registry.entries import SeedRegistryEntry
from scrapers.base.run_config import RunConfig

ExportCallable = Callable[..., None]


class FunctionExportRunner(LayerJobRunner):
    def __init__(
        self,
        *,
        export: ExportCallable | None = None,
        export_function: ExportCallable | None = None,
        component_metadata: RunnerMetadata,
    ) -> None:
        self._export = export or export_function
        if self._export is None:
            msg = "FunctionExportRunner requires `export` callable."
            raise ValueError(msg)
        self.COMPONENT_METADATA = component_metadata

    def run(
        self,
        seed: SeedRegistryEntry,
        run_config: RunConfig,
        base_wiki_dir: Path,
    ) -> None:
        self._export(
            output_dir=base_wiki_dir / seed.default_output_path,
            include_urls=run_config.include_urls,
        )
