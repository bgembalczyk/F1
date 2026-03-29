from pathlib import Path

from layers.orchestration.runners.layer_job import LayerJobRunner
from layers.orchestration.runners.metadata import build_runner_metadata
from layers.seed.registry.entries import SeedRegistryEntry
from scrapers.base.helpers.runner import run_and_export
from scrapers.base.run_config import RunConfig
from scrapers.grands_prix.complete_scraper import F1CompleteGrandPrixDataExtractor


class GrandPrixRunner(LayerJobRunner):
    COMPONENT_METADATA = build_runner_metadata("grands_prix")

    def run(
        self,
        seed: SeedRegistryEntry,
        run_config: RunConfig,
        _base_wiki_dir: Path,
    ) -> None:
        run_and_export(
            F1CompleteGrandPrixDataExtractor,
            seed.default_output_path,
            run_config=run_config,
        )
