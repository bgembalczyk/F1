from __future__ import annotations

from pathlib import Path
from typing import Protocol
from typing import runtime_checkable

from layers.orchestration.runtime_config import RuntimeConfig
from layers.seed.registry.entries import ListJobRegistryEntry
from layers.seed.registry.entries import SeedRegistryEntry


@runtime_checkable
class LayerOneRunnerProtocol(Protocol):
    def run(
        self,
        seed: SeedRegistryEntry,
        runtime_config: RuntimeConfig,
    ) -> None: ...


@runtime_checkable
class LayerZeroRunConfigFactoryProtocol(Protocol):
    def create_scraper_kwargs(self, job: ListJobRegistryEntry) -> dict[str, object]: ...


@runtime_checkable
class LayerExecutorProtocol(Protocol):
    def run(self, runtime_config: RuntimeConfig) -> None: ...


@runtime_checkable
class LayerZeroMergeServiceProtocol(Protocol):
    def merge(self, base_wiki_dir: Path) -> None: ...
