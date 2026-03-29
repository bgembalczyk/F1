from __future__ import annotations

from typing import Protocol


class ProgressReporter(Protocol):
    def started(self, scope: str, name: str) -> None:
        """Report started processing event."""

    def finished(self, scope: str, name: str) -> None:
        """Report finished processing event."""

    def skipped(self, scope: str, name: str, reason: str) -> None:
        """Report skipped processing event."""

    def warn(self, scope: str, name: str, message: str) -> None:
        """Report warning event."""


class StdoutProgressReporter:
    def started(self, scope: str, name: str) -> None:
        print(f"[{scope}] running  {name}")

    def finished(self, scope: str, name: str) -> None:
        print(f"[{scope}] finished {name}")

    def skipped(self, scope: str, name: str, reason: str) -> None:
        print(f"[{scope}] skipping {name}: {reason}")

    def warn(self, scope: str, name: str, message: str) -> None:
        print(f"[{scope}] warning {name}: {message}")
