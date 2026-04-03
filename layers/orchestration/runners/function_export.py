from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING

from layers.orchestration.runners.layer_job import LayerJobRunner
from scrapers.base.errors import normalize_pipeline_error

if TYPE_CHECKING:
    from layers.orchestration.runners.metadata import RunnerMetadata
    from layers.seed.registry import SeedRegistryEntry
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
        try:
            self._export_function(
                output_dir=base_wiki_dir / seed.default_output_path,
                include_urls=run_config.include_urls,
            )
        except Exception as exc:
            raise normalize_pipeline_error(
                exc,
                code="layer1.function_export_failed",
                message="Layer one function export failed.",
                domain=seed.output_category,
                source_name=self.COMPONENT_METADATA.seed_name,
            ) from exc
