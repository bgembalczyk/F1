from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Any
from typing import Callable


@dataclass(frozen=True)
class PipelineTraceEvent:
    event: str
    layer: str
    job: str
    status: str
    timestamp_utc: str
    details: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "event": self.event,
            "layer": self.layer,
            "job": self.job,
            "status": self.status,
            "timestamp_utc": self.timestamp_utc,
            "details": self.details,
        }


class PipelineTrace:
    def __init__(
        self,
        sink: Callable[[PipelineTraceEvent], None] | None = None,
    ) -> None:
        self._sink = sink if sink is not None else lambda _event: None

    def start_job(self, *, layer: str, job: str, **details: Any) -> PipelineTraceEvent:
        return self._emit(
            event="start_job",
            layer=layer,
            job=job,
            status="started",
            details=details,
        )

    def end_job(self, *, layer: str, job: str, **details: Any) -> PipelineTraceEvent:
        return self._emit(
            event="end_job",
            layer=layer,
            job=job,
            status="completed",
            details=details,
        )

    def skip_job(
        self,
        *,
        layer: str,
        job: str,
        reason: str,
        **details: Any,
    ) -> PipelineTraceEvent:
        return self._emit(
            event="skip_job",
            layer=layer,
            job=job,
            status="skipped",
            details={"reason": reason, **details},
        )

    def merge_start(self, *, layer: str, job: str = "merge", **details: Any) -> PipelineTraceEvent:
        return self._emit(
            event="merge_start",
            layer=layer,
            job=job,
            status="started",
            details=details,
        )

    def merge_end(self, *, layer: str, job: str = "merge", **details: Any) -> PipelineTraceEvent:
        return self._emit(
            event="merge_end",
            layer=layer,
            job=job,
            status="completed",
            details=details,
        )

    def _emit(
        self,
        *,
        event: str,
        layer: str,
        job: str,
        status: str,
        details: dict[str, Any],
    ) -> PipelineTraceEvent:
        trace_event = PipelineTraceEvent(
            event=event,
            layer=layer,
            job=job,
            status=status,
            timestamp_utc=datetime.now(tz=timezone.utc).isoformat(),
            details=details,
        )
        self._sink(trace_event)
        return trace_event


class JsonlPipelineTraceSink:
    def __init__(self, output_path: Path) -> None:
        self._output_path = output_path

    def __call__(self, event: PipelineTraceEvent) -> None:
        self._output_path.parent.mkdir(parents=True, exist_ok=True)
        with self._output_path.open("a", encoding="utf-8") as output_file:
            output_file.write(json.dumps(event.to_dict(), ensure_ascii=False))
            output_file.write("\n")
