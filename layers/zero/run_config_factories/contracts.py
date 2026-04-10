from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Protocol
from typing import runtime_checkable

from layers.seed.registry.entries import ListJobRegistryEntry


@runtime_checkable
class LayerZeroRunConfigFactoryProtocol(Protocol):
    def create_scraper_kwargs(
        self,
        job: ListJobRegistryEntry | None = None,
    ) -> dict[str, object]: ...


class LayerZeroRunConfigFactory(LayerZeroRunConfigFactoryProtocol, ABC):
    @abstractmethod
    def create_scraper_kwargs(
        self,
        job: ListJobRegistryEntry | None = None,
    ) -> dict[str, object]:
        """Build scraper kwargs for layer-zero list job."""
