from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any

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
class StepExecutionResult:
    status: str
    records: list[dict[str, Any]]
    errors: list[str]
    metrics: dict[str, Any]
    output_paths: dict[str, str]

    @property
    def source_path(self) -> Path | None:
        source = self.output_paths.get("source_path")
        return Path(source) if source else None

    @classmethod
    def empty(cls, *, status: str = "initialized") -> StepExecutionResult:
        return cls(
            status=status,
            records=[],
            errors=[],
            metrics={},
            output_paths={},
        )

    def with_updates(
        self,
        *,
        status: str | None = None,
        records: list[dict[str, Any]] | None = None,
        errors: list[str] | None = None,
        metrics: dict[str, Any] | None = None,
        output_paths: dict[str, str] | None = None,
    ) -> StepExecutionResult:
        next_metrics = dict(self.metrics)
        if metrics:
            next_metrics.update(metrics)

        next_paths = dict(self.output_paths)
        if output_paths:
            next_paths.update(output_paths)

        return StepExecutionResult(
            status=status or self.status,
            records=records if records is not None else self.records,
            errors=errors if errors is not None else self.errors,
            metrics=next_metrics,
            output_paths=next_paths,
        )


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
