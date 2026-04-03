from abc import ABC
from abc import abstractmethod
from pathlib import Path

from layers.seed.registry import SeedRegistryEntry
from scrapers.base.run_config import RunConfig


class LayerJobRunner(ABC):
    @abstractmethod
    def run(
        self,
        seed: SeedRegistryEntry,
        run_config: RunConfig,
        base_wiki_dir: Path,
    ) -> None:
        """Execute layer-one job for given seed."""
