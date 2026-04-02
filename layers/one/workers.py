from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from layers.orchestration.protocols import LayerOneRunnerProtocol
from layers.seed.registry.entries import SeedRegistryEntry
from scrapers.base.run_config import RunConfig


@dataclass(frozen=True)
class LayerOneRunnerSelectionInput:
    seed_name: str
    runner_map: dict[str, LayerOneRunnerProtocol]


class LayerOneRunnerSelector:
    def select(self, data: LayerOneRunnerSelectionInput) -> LayerOneRunnerProtocol | None:
        return data.runner_map.get(data.seed_name)


@dataclass(frozen=True)
class LayerOneSeedExecutionInput:
    seed: SeedRegistryEntry
    run_config: RunConfig
    base_wiki_dir: Path
    runner: LayerOneRunnerProtocol


class LayerOneSeedRunner:
    def run(self, data: LayerOneSeedExecutionInput) -> None:
        data.runner.run(data.seed, data.run_config, data.base_wiki_dir)
