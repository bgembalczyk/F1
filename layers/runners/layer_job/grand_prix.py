from pathlib import Path

from complete_extractor.complete_scraper_grands_prix import F1CompleteGrandPrixDataExtractor
from layers.runners.layer_job.base import LayerJobRunner
from layers.runners.metadata import build_runner_metadata
from layers.seed.registry.entries import SeedRegistryEntry
from scrapers.errors.pipeline.helpers import normalize_pipeline_error
from scrapers.run_config import RunConfig
from scrapers.runners.scraper_runner import ScraperRunner


class GrandPrixRunner(LayerJobRunner):
    role = "runner"
    domain = "grands_prix"
    stage = "layer_one"
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
                source_name=self.COMPONENT_METADATA["seed_name"],
            ) from exc
