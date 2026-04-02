from layers.orchestration.runners.layer_job import LayerJobRunner
from layers.orchestration.runners.metadata import build_runner_metadata
from layers.orchestration.runtime_config import RuntimeConfig
from layers.seed.registry.entries import SeedRegistryEntry
from scrapers.base.runner import ScraperRunner
from scrapers.grands_prix.complete_scraper import F1CompleteGrandPrixDataExtractor


class GrandPrixRunner(LayerJobRunner):
    COMPONENT_METADATA = build_runner_metadata("grands_prix")

    def run(
        self,
        seed: SeedRegistryEntry,
        runtime_config: RuntimeConfig,
    ) -> None:
        ScraperRunner(runtime_config.to_run_config()).run_and_export(
            F1CompleteGrandPrixDataExtractor,
            seed.default_output_path,
        )
