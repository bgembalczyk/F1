from abc import ABC
from abc import abstractmethod
from layers.orchestration.runtime_config import RuntimeConfig
from layers.seed.registry.entries import SeedRegistryEntry


class LayerJobRunner(ABC):
    @abstractmethod
    def run(
        self,
        seed: SeedRegistryEntry,
        runtime_config: RuntimeConfig,
    ) -> None:
        """Execute layer-one job for given seed."""
