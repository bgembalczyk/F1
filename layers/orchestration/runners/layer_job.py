from abc import ABC
from abc import abstractmethod
from pathlib import Path

from layers.orchestration.runners.metadata import RunnerMetadata
from layers.seed.registry.entries import SeedRegistryEntry
from scrapers.base.run_config import RunConfig


class LayerJobRunner(ABC):
    @property
    @abstractmethod
    def metadata(self) -> RunnerMetadata:
        """Typed runner metadata used by layer-one orchestration and discovery."""

    @abstractmethod
    def run(
        self,
        seed: SeedRegistryEntry,
        run_config: RunConfig,
        base_wiki_dir: Path,
    ) -> None:
        """Execute layer-one job for given seed."""
