from __future__ import annotations

from pathlib import Path

from layers.orchestration.pipeline_trace import JsonlPipelineTraceSink
from layers.orchestration.pipeline_trace import PipelineTrace
from layers.orchestration.protocols import LayerExecutorProtocol
from layers.zero.helpers import build_debug_run_config
from scrapers.base.run_config import RunConfig


class WikiPipelineApplication:
    def __init__(
        self,
        *,
        base_wiki_dir: Path,
        base_debug_dir: Path,
        layer_zero_executor: LayerExecutorProtocol,
        layer_one_executor: LayerExecutorProtocol,
        pipeline_trace: PipelineTrace | None = None,
        diagnostic_trace_path: Path | None = None,
    ) -> None:
        self._base_wiki_dir = base_wiki_dir
        self._base_debug_dir = base_debug_dir
        self._layer_zero_executor = layer_zero_executor
        self._layer_one_executor = layer_one_executor
        self._pipeline_trace = self._build_pipeline_trace(
            pipeline_trace=pipeline_trace,
            diagnostic_trace_path=diagnostic_trace_path,
        )

    def _build_pipeline_trace(
        self,
        *,
        pipeline_trace: PipelineTrace | None,
        diagnostic_trace_path: Path | None,
    ) -> PipelineTrace:
        if pipeline_trace is not None:
            return pipeline_trace
        if diagnostic_trace_path is not None:
            return PipelineTrace(sink=JsonlPipelineTraceSink(diagnostic_trace_path))
        return PipelineTrace()

    def _build_run_config(self, *, profile: str = "debug") -> RunConfig:
        if profile == "debug":
            return build_debug_run_config(
                base_wiki_dir=self._base_wiki_dir,
                base_debug_dir=self._base_debug_dir,
            )
        raise ValueError(profile)

    def run_layer_zero(self) -> None:
        self._pipeline_trace.start_job(layer="pipeline", job="layer_zero")
        run_config = self._build_run_config()
        self._layer_zero_executor.run(run_config, self._base_wiki_dir)
        self._pipeline_trace.end_job(layer="pipeline", job="layer_zero")

    def run_layer_one(self) -> None:
        self._pipeline_trace.start_job(layer="pipeline", job="layer_one")
        run_config = self._build_run_config()
        self._layer_one_executor.run(run_config, self._base_wiki_dir)
        self._pipeline_trace.end_job(layer="pipeline", job="layer_one")
