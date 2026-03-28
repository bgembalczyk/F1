from pathlib import Path

from layers.orchestration.runners.layer_job import LayerJobRunner
from layers.seed.registry.entries import SeedRegistryEntry
from scrapers.base.run_config import RunConfig
from scrapers.constructors.helpers.export import export_complete_constructors


class ConstructorsRunner(LayerJobRunner):
    COMPONENT_METADATA = {
        "domain": "constructors",
        "seed_name": "constructors",
        "layer": "layer_one",
        "output_category": "constructors",
        "component_type": "runner",
    }

    def run(
        self,
        seed: SeedRegistryEntry,
        run_config: RunConfig,
        base_wiki_dir: Path,
    ) -> None:
        export_complete_constructors(
            output_dir=base_wiki_dir / seed.default_output_path,
            include_urls=run_config.include_urls,
        )
