from pathlib import Path

from layers.one.executor import LayerOneExecutor
from layers.zero.executor import LayerZeroExecutor
from layers.zero.helpers import build_debug_run_config


class WikiPipelineApplication:
    def __init__(
        self,
        *,
        base_wiki_dir: Path,
        base_debug_dir: Path,
        layer_zero_executor: LayerZeroExecutor,
        layer_one_executor: LayerOneExecutor,
    ) -> None:
        self._base_wiki_dir = base_wiki_dir
        self._base_debug_dir = base_debug_dir
        self._layer_zero_executor = layer_zero_executor
        self._layer_one_executor = layer_one_executor

    def _build_run_config(self, *, profile: str = "debug"):
        """Build run config for selected execution profile."""
        if profile == "debug":
            return build_debug_run_config(
                base_wiki_dir=self._base_wiki_dir,
                base_debug_dir=self._base_debug_dir,
            )

        raise ValueError(f"Unsupported run config profile: {profile}")

    def run_layer_zero(self) -> None:
        run_config = self._build_run_config(profile="debug")
        self._layer_zero_executor.run(run_config, self._base_wiki_dir)

    def run_layer_one(self) -> None:
        run_config = self._build_run_config(profile="debug")
        self._layer_one_executor.run(run_config, self._base_wiki_dir)
