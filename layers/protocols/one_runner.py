from typing import Protocol
from typing import runtime_checkable

from pathlib import Path

from layers.seed.registry.entries import SeedRegistryEntry
from scrapers.run_config import RunConfig


@runtime_checkable
class LayerOneRunnerProtocol(Protocol):
    def run(
        self,
        seed: SeedRegistryEntry,
        run_config: RunConfig,
        base_wiki_dir: Path,
    ) -> None: ...
