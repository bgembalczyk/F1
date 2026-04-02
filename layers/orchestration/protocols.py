from __future__ import annotations

from pathlib import Path
from typing import Protocol
from typing import runtime_checkable

from layers.orchestration.contracts import LayerExecutionRequestDTO
from layers.orchestration.contracts import LayerExecutionResultDTO
from layers.orchestration.contracts import LayerZeroMergeRequestDTO
from layers.orchestration.contracts import LayerZeroMergeResultDTO
from layers.seed.registry.entries import ListJobRegistryEntry
from layers.seed.registry.entries import SeedRegistryEntry
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
    def run(
        self,
        request: LayerExecutionRequestDTO | RunConfig,
        base_wiki_dir: Path | None = None,
    ) -> LayerExecutionResultDTO: ...


@runtime_checkable
class LayerZeroMergeServiceProtocol(Protocol):
    def merge(
        self,
        request: LayerZeroMergeRequestDTO | Path,
    ) -> LayerZeroMergeResultDTO: ...
