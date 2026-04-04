from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Literal

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

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

    def run_full(self) -> None:
        self.layer_zero_executor.run(self.run_config_factory(), self.base_wiki_dir)
        self.layer_one_executor.run(self.run_config_factory(), self.base_wiki_dir)

    def run_scenario(self, scenario: WikiRunScenario) -> None:
        if scenario == "layer0":
            self.layer_zero_executor.run(self.run_config_factory(), self.base_wiki_dir)
            return
        if scenario == "layer1":
            self.layer_one_executor.run(self.run_config_factory(), self.base_wiki_dir)
            return
        if scenario == "merge":
            self.layer_zero_merge_service.merge(self.base_wiki_dir)
            return
        if scenario == "full":
            self.run_full()
            return
        msg = f"Unsupported wiki run scenario: {scenario!r}"
        raise ValueError(msg)
