from pathlib import Path
from typing import TYPE_CHECKING

from scrapers.core.logging import RunTraceWriter

if TYPE_CHECKING:
    from scrapers.core.run_config import RunConfig


class BaseExecutor:
    def _build_trace_writer(
        self,
        *,
        run_config: "RunConfig",
        run_id: str,
        layer: int,
    ) -> RunTraceWriter:
        debug_root = (
            Path(run_config.debug_dir)
            if run_config.debug_dir
            else Path(run_config.output_dir)
        )
        trace_path = debug_root / "traces" / f"layer{layer}_{run_id}.jsonl"
        timestamp_provider = (
            (lambda: run_config.fixed_timestamp)
            if run_config.fixed_timestamp is not None
            else None
        )
        return RunTraceWriter(trace_path, timestamp_provider=timestamp_provider)
