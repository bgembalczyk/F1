from pathlib import Path

from layers.orchestration.protocols import LayerExecutorProtocol
from layers.pipeline_workers import RunConfigBuildInput
from layers.pipeline_workers import RunConfigBuilderWorker
from scrapers.base.run_config import RunConfig


class WikiPipelineApplication:
    def __init__(
        self,
        *,
        base_wiki_dir: Path,
        base_debug_dir: Path,
        layer_zero_executor: LayerExecutorProtocol,
        layer_one_executor: LayerExecutorProtocol,
        run_config_builder: RunConfigBuilderWorker | None = None,
    ) -> None:
        self._base_wiki_dir = base_wiki_dir
        self._base_debug_dir = base_debug_dir
        self._layer_zero_executor = layer_zero_executor
        self._layer_one_executor = layer_one_executor
        self._run_config_builder = run_config_builder or RunConfigBuilderWorker()

    def _build_run_config(self, *, profile: str = "debug") -> RunConfig:
        return self._run_config_builder.build(
            RunConfigBuildInput(
                profile=profile,
                base_wiki_dir=self._base_wiki_dir,
                base_debug_dir=self._base_debug_dir,
            ),
        )

    def run_layer_zero(self) -> None:
        run_config = self._build_run_config()
        try:
            self._layer_zero_executor.run(run_config, self._base_wiki_dir)
        except Exception as exc:
            raise RuntimeError("layer zero orchestration failed") from exc

    def run_layer_one(self) -> None:
        run_config = self._build_run_config()
        try:
            self._layer_one_executor.run(run_config, self._base_wiki_dir)
        except Exception as exc:
            raise RuntimeError("layer one orchestration failed") from exc
