from pathlib import Path

from layers.orchestration.runners.layer_job import LayerJobRunner
from layers.orchestration.runners.metadata import build_runner_metadata
from layers.seed.registry.entries import SeedRegistryEntry
from scrapers.base.errors import normalize_pipeline_error
from scrapers.base.run_config import RunConfig
from scrapers.base.runner import ScraperRunner
from scrapers.grands_prix.complete_scraper import F1CompleteGrandPrixDataExtractor


class GrandPrixRunner(LayerJobRunner):
    COMPONENT_METADATA = build_runner_metadata("grands_prix")

    def run(
        self,
        seed: SeedRegistryEntry,
        run_config: RunConfig,
        _base_wiki_dir: Path,
    ) -> None:
        try:
            ScraperRunner(run_config).run_and_export(
                F1CompleteGrandPrixDataExtractor,
                seed.default_output_path,
            )
        except Exception as exc:
            raise normalize_pipeline_error(
                exc,
                code="layer1.grand_prix_failed",
                message="Grand prix export failed.",
                domain=seed.output_category,
                source_name=self.COMPONENT_METADATA.seed_name,
            ) from exc
