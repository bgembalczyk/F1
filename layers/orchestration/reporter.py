from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class LayerExecutionReporterProtocol(Protocol):
    def started(self, *, layer: str, step: str) -> None: ...

    def finished(self, *, layer: str, step: str) -> None: ...

    def skipped(self, *, layer: str, step: str, reason: str) -> None: ...


@dataclass(frozen=True)
class ConsoleLayerExecutionReporter:
    def started(self, *, layer: str, step: str) -> None:
        print(f"[{layer}] started {step}")

    def finished(self, *, layer: str, step: str) -> None:
        print(f"[{layer}] finished {step}")

    def skipped(self, *, layer: str, step: str, reason: str) -> None:
        print(f"[{layer}] skipped {step}: {reason}")
