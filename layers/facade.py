from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from layers.orchestration.protocols import LayerExecutorProtocol
from layers.orchestration.protocols import LayerZeroMergeServiceProtocol
from scrapers.base.run_config import RunConfig

WikiRunScenario = Literal["layer0", "layer1", "full", "merge"]


@dataclass(frozen=True)
class WikiPipelineFacade:
    """Single high-level entrypoint for common wiki pipeline run scenarios."""

    base_wiki_dir: Path
    base_debug_dir: Path
    layer_zero_executor: LayerExecutorProtocol
    layer_one_executor: LayerExecutorProtocol
    layer_zero_merge_service: LayerZeroMergeServiceProtocol
    run_config_factory: Callable[[], RunConfig]

    def run_layer_zero(self) -> None:
        self.layer_zero_executor.run(self._build_run_config(), self.base_wiki_dir)

    def run_layer_one(self) -> None:
        self.layer_one_executor.run(self._build_run_config(), self.base_wiki_dir)

    def run_full(self) -> None:
        self.run_layer_zero()
        self.run_layer_one()

    def run_merge_only(self) -> None:
        self.layer_zero_merge_service.merge(self.base_wiki_dir)

    def run_scenario(self, scenario: WikiRunScenario) -> None:
        if scenario == "layer0":
            self.run_layer_zero()
            return
        if scenario == "layer1":
            self.run_layer_one()
            return
        if scenario == "merge":
            self.run_merge_only()
            return
        if scenario == "full":
            self.run_full()
            return
        raise ValueError(f"Unsupported wiki run scenario: {scenario!r}")

    def _build_run_config(self) -> RunConfig:
        return self.run_config_factory()
