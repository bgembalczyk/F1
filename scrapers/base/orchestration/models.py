from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any
from typing import Protocol

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True)
class OrchestrationPaths:
    base_dir: Path

    @property
    def raw(self) -> Path:
        return self.base_dir / "raw"

    @property
    def checkpoints(self) -> Path:
        return self.base_dir / "checkpoints"

    @property
    def legacy_wiki(self) -> Path:
        return self.base_dir / "wiki"

    def checkpoint_file(self, filename: str) -> Path:
        return self.checkpoints / filename


@dataclass(frozen=True)
class StepDeclaration:
    step_id: int
    layer: str
    input_source: str
    parser: Callable[[list[dict[str, Any]]], list[dict[str, Any]]]
    output_target: str


@dataclass(frozen=True)
class ResolvedInput:
    records: list[dict[str, Any]]
    source_path: Path


@dataclass(frozen=True)
class ExecutedStep:
    records: list[dict[str, Any]]
    errors: list[str]
    duration_ms: float


@dataclass(frozen=True)
class CheckpointMetrics:
    input_records: int
    output_records: int
    errors: int
    duration_ms: float
    input_path: str


@dataclass(frozen=True)
class CheckpointMetadata:
    step_id: int
    layer: str
    domain: str
    input_source: str
    output_target: str
    parser: str
    generated_at: str
    metrics: CheckpointMetrics


@dataclass(frozen=True)
class CheckpointPayload:
    metadata: CheckpointMetadata
    records: list[dict[str, Any]]


@dataclass(frozen=True)
class StepExecutionResult:
    step: StepDeclaration
    domain: str
    input_path: str
    output_path: str
    input_records: int
    output_records: int
    errors: list[str]
    duration_ms: float


@dataclass(frozen=True)
class AuditEntry:
    timestamp: str
    step_id: int
    layer: str
    domain: str
    input_path: str
    output_path: str
    input_records: int
    output_records: int
    errors: list[str]
    duration_ms: float


class InputResolver(Protocol):
    def resolve(self, step: StepDeclaration, domain: str) -> ResolvedInput:
        """Resolve step input records and source path."""


class StepExecutor(Protocol):
    def execute(
        self,
        step: StepDeclaration,
        input_records: list[dict[str, Any]],
    ) -> ExecutedStep:
        """Execute parser for step and return normalized execution outcome."""


class CheckpointRepository(Protocol):
    def save(
        self,
        step: StepDeclaration,
        domain: str,
        input_path: Path,
        input_records: list[dict[str, Any]],
        execution: ExecutedStep,
    ) -> Path:
        """Persist checkpoint payload for a step and return output path."""


class AuditRepository(Protocol):
    def append(self, entry: AuditEntry) -> None:
        """Append audit row for step execution."""

    def write_regression_report(self, report_path: Path) -> Path:
        """Persist aggregated audit report and return path."""
