from pathlib import Path

from layers.orchestration.runners.layer_job import LayerJobRunner
from layers.orchestration.runners.metadata import RunnerMetadata
from layers.seed.registry.entries import SeedRegistryEntry
from scrapers.base.run_config import RunConfig
from scrapers.circuits.helpers.export import export_complete_circuits


class CircuitsRunner(LayerJobRunner):
    _METADATA = RunnerMetadata.build(domain="circuits")

    @property
    def metadata(self) -> RunnerMetadata:
        return self._METADATA

    def run(
        self,
        seed: SeedRegistryEntry,
        run_config: RunConfig,
        base_wiki_dir: Path,
    ) -> None:
        export_complete_circuits(
            output_dir=base_wiki_dir / seed.default_output_path,
            include_urls=run_config.include_urls,
        )
