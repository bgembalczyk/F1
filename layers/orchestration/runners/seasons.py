from pathlib import Path

from layers.orchestration.runners.layer_job import LayerJobRunner
from layers.seed.registry.entries import SeedRegistryEntry
from scrapers.base.run_config import RunConfig
from scrapers.seasons.helpers import export_complete_seasons


class SeasonsRunner(LayerJobRunner):
    COMPONENT_METADATA = {
        "domain": "seasons",
        "seed_name": "seasons",
        "layer": "layer_one",
        "output_category": "seasons",
        "component_type": "runner",
    }

    def run(
        self,
        seed: SeedRegistryEntry,
        run_config: RunConfig,
        base_wiki_dir: Path,
    ) -> None:
        export_complete_seasons(
            output_dir=base_wiki_dir / seed.default_output_path,
            include_urls=run_config.include_urls,
        )
