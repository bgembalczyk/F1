from pathlib import Path

from layers.orchestration.protocols import LayerExecutorProtocol
from layers.zero.run_profile_paths import build_debug_run_config
from scrapers.base.run_config import RunConfig


class WikiPipelineApplication:
    def __init__(
        self,
        *,
        base_wiki_dir: Path,
        base_debug_dir: Path,
        layer_zero_executor: LayerExecutorProtocol,
        layer_one_executor: LayerExecutorProtocol,
    ) -> None:
        self._base_wiki_dir = base_wiki_dir
        self._base_debug_dir = base_debug_dir
        self._layer_zero_executor = layer_zero_executor
        self._layer_one_executor = layer_one_executor

    def _build_run_config(self, *, profile: str = "debug") -> RunConfig:
        if profile == "debug":
            return build_debug_run_config(
                base_wiki_dir=self._base_wiki_dir,
                base_debug_dir=self._base_debug_dir,
            )
        raise ValueError(profile)

    def run_layer_zero(self) -> None:
        run_config = self._build_run_config()
        self._layer_zero_executor.run(run_config, self._base_wiki_dir)

    def run_layer_one(self) -> None:
        run_config = self._build_run_config()
        self._layer_one_executor.run(run_config, self._base_wiki_dir)
