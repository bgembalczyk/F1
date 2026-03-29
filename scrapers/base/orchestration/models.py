from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

OrchestrationRecord = dict[str, object]
OrchestrationRecords = list[OrchestrationRecord]


def normalize_orchestration_payload(payload: object) -> OrchestrationRecords:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        records = payload.get("records", [])
        if isinstance(records, list):
            return [item for item in records if isinstance(item, dict)]
    return []


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
    parser: Callable[[OrchestrationRecords], OrchestrationRecords]
    output_target: str


@dataclass(frozen=True)
class ResolvedInput:
    records: OrchestrationRecords
    source_path: Path


@dataclass(frozen=True)
class ExecutedStep:
    records: OrchestrationRecords
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
    records: OrchestrationRecords


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
