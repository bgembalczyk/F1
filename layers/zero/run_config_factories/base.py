from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from layers.seed.registry.entries import ListJobRegistryEntry


class LayerZeroRunConfigFactory(ABC):
    @abstractmethod
    def create_scraper_kwargs(
        self,
        job: ListJobRegistryEntry | None = None,
    ) -> dict[str, object]:
        """Build scraper kwargs for layer-zero list job."""
