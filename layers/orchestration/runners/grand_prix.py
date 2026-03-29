from pathlib import Path

from layers.orchestration.runners.layer_job import LayerJobRunner
from layers.orchestration.runners.metadata import build_runner_metadata
from layers.seed.registry.entries import SeedRegistryEntry
from scrapers.base.run_config import RunConfig
from scrapers.base.runner import ScraperRunner
from scrapers.grands_prix.complete_scraper import F1CompleteGrandPrixDataExtractor


class GrandPrixRunner(LayerJobRunner):
    COMPONENT_METADATA = build_runner_metadata(domain="grands_prix")

    def run(
        self,
        seed: SeedRegistryEntry,
        run_config: RunConfig,
        _base_wiki_dir: Path,
    ) -> None:
        ScraperRunner(run_config).run_and_export(
            F1CompleteGrandPrixDataExtractor,
            seed.default_output_path,
        )
