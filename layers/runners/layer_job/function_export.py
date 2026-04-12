from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from layers.runners.layer_job.base import LayerJobRunner
from layers.runners.metadata import RunnerMetadata
from layers.seed.registry.entries import SeedRegistryEntry
from scrapers.errors.pipeline.helpers import normalize_pipeline_error
from scrapers.run_config import RunConfig

if TYPE_CHECKING:
    from pathlib import Path


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
            self._export(
                output_dir=base_wiki_dir / seed.default_output_path,
                include_urls=run_config.include_urls,
            )
        except Exception as exc:
            raise normalize_pipeline_error(
                exc,
                code="layer1.function_export_failed",
                message="Layer one function export failed.",
                domain=seed.output_category,
                source_name=self.COMPONENT_METADATA["seed_name"],
            ) from exc
