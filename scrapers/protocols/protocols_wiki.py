from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from layers.seed.registry import SeedRegistryEntry
    from scrapers.run_config import RunConfig


class ListScraperConfigABC(ABC):
    url: str


class DiscoveredListScraperClassABC(ABC):
    CONFIG: ListScraperConfigABC


class DiscoveredRunnerABC(ABC):
    @abstractmethod
    def run(
        self,
        seed: SeedRegistryEntry,
        run_config: RunConfig,
        base_wiki_dir: Path,
    ) -> None: ...


class DiscoveredRunnerClassABC(ABC):
    @abstractmethod
    def __call__(self) -> DiscoveredRunnerABC: ...


__all__ = [
    "DiscoveredListScraperClassABC",
    "DiscoveredRunnerABC",
    "DiscoveredRunnerClassABC",
    "ListScraperConfigABC",
]
