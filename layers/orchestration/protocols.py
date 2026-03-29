from __future__ import annotations

from pathlib import Path
from typing import Protocol

from layers.seed.registry.entries import ListJobRegistryEntry
from layers.seed.registry.entries import SeedRegistryEntry
from scrapers.base.run_config import RunConfig


class LayerOneRunnerProtocol(Protocol):
    def run(
        self,
        seed: SeedRegistryEntry,
        run_config: RunConfig,
        base_wiki_dir: Path,
    ) -> None: ...


class LayerZeroRunConfigFactoryProtocol(Protocol):
    def create_scraper_kwargs(self, job: ListJobRegistryEntry) -> dict[str, object]: ...
