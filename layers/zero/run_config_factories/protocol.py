from typing import Protocol
from typing import runtime_checkable

from layers.seed.registry.entries import ListJobRegistryEntry


@runtime_checkable
class LayerZeroRunConfigFactoryProtocol(Protocol):
    def create_scraper_kwargs(self, job: ListJobRegistryEntry) -> dict[str, object]: ...
