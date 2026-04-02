from pathlib import Path

from layers.orchestration.protocols import LayerExecutorProtocol
from layers.orchestration.runtime_config import RuntimeConfig
from layers.orchestration.runtime_config import WikiMode


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

    def _build_runtime_config(self, *, mode: WikiMode) -> RuntimeConfig:
        return RuntimeConfig(
            base_wiki_dir=self._base_wiki_dir,
            base_debug_dir=self._base_debug_dir,
            mode=mode,
        )

    def run_layer_zero(self, runtime_config: RuntimeConfig | None = None) -> None:
        runtime_config = runtime_config or self._build_runtime_config(mode="layer0")
        self._layer_zero_executor.run(runtime_config)

    def run_layer_one(self, runtime_config: RuntimeConfig | None = None) -> None:
        runtime_config = runtime_config or self._build_runtime_config(mode="layer1")
        self._layer_one_executor.run(runtime_config)
