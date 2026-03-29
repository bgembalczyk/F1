from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class PipelineEvent:
    phase: str
    layer: str
    step_type: str
    step_name: str
    message: str | None = None


class PipelineStepReporterProtocol(Protocol):
    def start(self, *, layer: str, step_type: str, step_name: str) -> None: ...

    def finish(self, *, layer: str, step_type: str, step_name: str) -> None: ...

    def skip(
        self,
        *,
        layer: str,
        step_type: str,
        step_name: str,
        reason: str,
    ) -> None: ...


class ConsolePipelineStepReporter:
    def _emit(self, event: PipelineEvent) -> None:
        base = (
            f"[pipeline] {event.phase} "
            f"layer={event.layer} type={event.step_type} step={event.step_name}"
        )
        if event.message:
            print(f"{base} message={event.message}")
            return
        print(base)

    def start(self, *, layer: str, step_type: str, step_name: str) -> None:
        self._emit(
            PipelineEvent(
                phase="start",
                layer=layer,
                step_type=step_type,
                step_name=step_name,
            ),
        )

    def finish(self, *, layer: str, step_type: str, step_name: str) -> None:
        self._emit(
            PipelineEvent(
                phase="finish",
                layer=layer,
                step_type=step_type,
                step_name=step_name,
            ),
        )

    def skip(
        self,
        *,
        layer: str,
        step_type: str,
        step_name: str,
        reason: str,
    ) -> None:
        self._emit(
            PipelineEvent(
                phase="skip",
                layer=layer,
                step_type=step_type,
                step_name=step_name,
                message=reason,
            ),
        )


class NullPipelineStepReporter:
    def start(self, *, layer: str, step_type: str, step_name: str) -> None:
        return None

    def finish(self, *, layer: str, step_type: str, step_name: str) -> None:
        return None

    def skip(
        self,
        *,
        layer: str,
        step_type: str,
        step_name: str,
        reason: str,
    ) -> None:
        return None
