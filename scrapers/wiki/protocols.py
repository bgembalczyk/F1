from __future__ import annotations

from pathlib import Path
from typing import Protocol
from typing import runtime_checkable

from layers.seed.registry.entries import SeedRegistryEntry
from scrapers.base.run_config import RunConfig


class ListScraperConfigProtocol(Protocol):
    url: str


class DiscoveredListScraperClassProtocol(Protocol):
    CONFIG: ListScraperConfigProtocol


@runtime_checkable
class DiscoveredRunnerProtocol(Protocol):
    def run(
        self,
        seed: SeedRegistryEntry,
        run_config: RunConfig,
        base_wiki_dir: Path,
    ) -> None: ...


class DiscoveredRunnerClassProtocol(Protocol):
    def __call__(self) -> DiscoveredRunnerProtocol: ...
