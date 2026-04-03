from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from typing import Protocol
from typing import runtime_checkable

if TYPE_CHECKING:
    from pathlib import Path

    from layers.seed.registry import ListJobRegistryEntry
    from layers.seed.registry import SeedRegistryEntry
    from scrapers.base.run_config import RunConfig


@runtime_checkable
class LayerOneRunnerProtocol(Protocol):
    def run(
        self,
        seed: SeedRegistryEntry,
        run_config: RunConfig,
        base_wiki_dir: Path,
    ) -> None: ...


@runtime_checkable
class LayerZeroRunConfigFactoryProtocol(Protocol):
    def create_scraper_kwargs(self, job: ListJobRegistryEntry) -> dict[str, object]: ...


@runtime_checkable
class LayerExecutorProtocol(Protocol):
    def run(self, run_config: RunConfig, base_wiki_dir: Path) -> None: ...


@runtime_checkable
class LayerZeroMergeServiceProtocol(Protocol):
    def merge(self, base_wiki_dir: Path) -> None: ...
