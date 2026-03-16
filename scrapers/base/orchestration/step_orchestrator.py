from __future__ import annotations

import csv
import json
import time
from dataclasses import asdict
from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any
from typing import Protocol

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True)
class _OrchestrationPaths:
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
    def execute(self, step: StepDeclaration, input_records: list[dict[str, Any]]) -> ExecutedStep:
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


class SectionSourceAdapter:
    """Pobiera wejście dla kroku z checkpointów i fallbackiem do raw."""

    def __init__(self, base_dir: Path = Path("data")) -> None:
        self.base_dir = base_dir
        self.paths = _OrchestrationPaths(base_dir=base_dir)

    def resolve(
        self,
        step: StepDeclaration,
        domain: str,
    ) -> ResolvedInput:
        direct_path = Path(step.input_source)
        if direct_path.is_absolute() and direct_path.exists():
            return ResolvedInput(records=self._read_records(direct_path), source_path=direct_path)

        checkpoint_path = self._resolve_checkpoint(step, domain)
        if checkpoint_path is not None:
            return ResolvedInput(records=self._read_records(checkpoint_path), source_path=checkpoint_path)

        raw_path = self._resolve_raw(step, domain)
        if raw_path is not None:
            return ResolvedInput(records=self._read_records(raw_path), source_path=raw_path)

        msg = (
            "Brak źródła wejścia dla "
            f"kroku={step.step_id}, source={step.input_source}"
        )
        raise FileNotFoundError(msg)

    def _resolve_checkpoint(self, step: StepDeclaration, domain: str) -> Path | None:
        checkpoints_dir = self.paths.checkpoints
        explicit = checkpoints_dir / f"{step.input_source}.json"
        if explicit.exists():
            return explicit

        wildcard = sorted(
            checkpoints_dir.glob(
                f"*{step.input_source}*{domain}*.json",
            ),
        )
        if wildcard:
            return wildcard[-1]

        layer_match = sorted(
            checkpoints_dir.glob(
                f"step_*_{step.layer}_{domain}.json",
            ),
        )
        if layer_match:
            return layer_match[-1]
        return None

    def _resolve_raw(self, step: StepDeclaration, domain: str) -> Path | None:
        raw_dir = self.paths.raw
        candidates = [
            raw_dir / f"{step.input_source}.json",
            raw_dir / domain / f"{step.input_source}.json",
            raw_dir / domain / f"{domain}.json",
            self.paths.legacy_wiki / domain / f"{step.input_source}.json",
            self.paths.legacy_wiki / domain / f"{domain}.json",
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate

        wildcard = sorted(raw_dir.glob(f"**/*{domain}*.json"))
        if wildcard:
            return wildcard[-1]
        return None

    @staticmethod
    def _read_records(path: Path) -> list[dict[str, Any]]:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        if isinstance(payload, dict):
            records = payload.get("records", [])
            if isinstance(records, list):
                return [item for item in records if isinstance(item, dict)]
        return []


class ParserStepExecutor:
    def execute(self, step: StepDeclaration, input_records: list[dict[str, Any]]) -> ExecutedStep:
        errors: list[str] = []
        started_at = time.perf_counter()
        try:
            output_records = step.parser(input_records)
        except Exception as exc:  # noqa: BLE001
            output_records = []
            errors.append(str(exc))

        duration_ms = (time.perf_counter() - started_at) * 1000
        return ExecutedStep(records=output_records, errors=errors, duration_ms=duration_ms)


class CheckpointPayloadFactory:
    def build(
        self,
        *,
        step: StepDeclaration,
        domain: str,
        input_path: Path,
        input_records: list[dict[str, Any]],
        execution: ExecutedStep,
    ) -> CheckpointPayload:
        return CheckpointPayload(
            metadata=CheckpointMetadata(
                step_id=step.step_id,
                layer=step.layer,
                domain=domain,
                input_source=str(input_path),
                output_target=step.output_target,
                parser=step.parser.__name__,
                generated_at=datetime.now(tz=timezone.utc).isoformat(),
                metrics=CheckpointMetrics(
                    input_records=len(input_records),
                    output_records=len(execution.records),
                    errors=len(execution.errors),
                    duration_ms=execution.duration_ms,
                    input_path=str(input_path),
                ),
            ),
            records=execution.records,
        )


class JsonCheckpointRepository:
    def __init__(
        self,
        *,
        base_dir: Path = Path("data"),
        payload_factory: CheckpointPayloadFactory | None = None,
    ) -> None:
        self.paths = _OrchestrationPaths(base_dir=base_dir)
        self.payload_factory = payload_factory or CheckpointPayloadFactory()

    def save(
        self,
        step: StepDeclaration,
        domain: str,
        input_path: Path,
        input_records: list[dict[str, Any]],
        execution: ExecutedStep,
    ) -> Path:
        output_path = self._output_path(step, domain)
        payload = self.payload_factory.build(
            step=step,
            domain=domain,
            input_path=input_path,
            input_records=input_records,
            execution=execution,
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(asdict(payload), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return output_path

    def _output_path(self, step: StepDeclaration, domain: str) -> Path:
        name = f"step_{step.step_id}_{step.layer}_{domain}.json"
        return self.paths.checkpoint_file(name)


class StepAuditTrail:
    def __init__(self, json_path: Path, csv_path: Path) -> None:
        self.json_path = json_path
        self.csv_path = csv_path

    def append(self, entry: AuditEntry) -> None:
        data = self._load_json()
        data.append(asdict(entry))
        self.json_path.parent.mkdir(parents=True, exist_ok=True)
        self.json_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        self.csv_path.parent.mkdir(parents=True, exist_ok=True)
        write_header = not self.csv_path.exists()
        with self.csv_path.open("a", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "timestamp",
                    "step_id",
                    "layer",
                    "domain",
                    "input_path",
                    "output_path",
                    "input_records",
                    "output_records",
                    "errors",
                    "duration_ms",
                ],
            )
            if write_header:
                writer.writeheader()
            row = asdict(entry)
            row["errors"] = " | ".join(entry.errors)
            writer.writerow(row)

    def write_regression_report(self, report_path: Path) -> Path:
        entries = self._load_json()
        total_steps = len(entries)
        total_errors = sum(1 for entry in entries if entry.get("errors"))
        total_duration = sum(float(entry.get("duration_ms", 0.0)) for entry in entries)

        grouped: dict[tuple[int, str, str], dict[str, Any]] = {}
        for entry in entries:
            key = (
                int(entry.get("step_id", -1)),
                str(entry.get("layer", "")),
                str(entry.get("domain", "")),
            )
            bucket = grouped.setdefault(
                key,
                {
                    "runs": 0,
                    "input_records": 0,
                    "output_records": 0,
                    "errors": 0,
                    "duration_ms": 0.0,
                },
            )
            bucket["runs"] += 1
            bucket["input_records"] += int(entry.get("input_records", 0))
            bucket["output_records"] += int(entry.get("output_records", 0))
            bucket["duration_ms"] += float(entry.get("duration_ms", 0.0))
            if entry.get("errors"):
                bucket["errors"] += 1

        lines = [
            "# Step Regression Audit Report",
            "",
            f"- Total runs: {total_steps}",
            f"- Total error runs: {total_errors}",
            f"- Total duration [ms]: {total_duration:.3f}",
            "",
            "| step_id | layer | domain | runs | input_records | output_records | error_runs | duration_ms |",
            "|---:|---|---|---:|---:|---:|---:|---:|",
        ]

        for (step_id, layer, domain), data in sorted(grouped.items()):
            lines.append(
                "| "
                f"{step_id} | {layer} | {domain} | {data['runs']} | "
                f"{data['input_records']} | {data['output_records']} | "
                f"{data['errors']} | {data['duration_ms']:.3f} |"
            )

        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return report_path

    def _load_json(self) -> list[dict[str, Any]]:
        if not self.json_path.exists():
            return []
        payload = json.loads(self.json_path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            return []
        return payload


class StepOrchestrator:
    def __init__(
        self,
        *,
        base_dir: Path = Path("data"),
        input_resolver: InputResolver | None = None,
        step_executor: StepExecutor | None = None,
        checkpoint_repository: CheckpointRepository | None = None,
        audit_repository: AuditRepository | None = None,
        source_adapter: SectionSourceAdapter | None = None,
        audit_trail: StepAuditTrail | None = None,
    ) -> None:
        self.base_dir = base_dir
        self.paths = _OrchestrationPaths(base_dir=base_dir)
        resolved_input = input_resolver or source_adapter
        resolved_audit = audit_repository or audit_trail
        self.input_resolver = resolved_input or SectionSourceAdapter(base_dir=base_dir)
        self.step_executor = step_executor or ParserStepExecutor()
        self.checkpoint_repository = checkpoint_repository or JsonCheckpointRepository(base_dir=base_dir)
        self.audit_repository = resolved_audit or StepAuditTrail(
            json_path=self.paths.checkpoint_file("step_audit.json"),
            csv_path=self.paths.checkpoint_file("step_audit.csv"),
        )
        # Backward-compatible alias for existing callers.
        self.audit_trail = self.audit_repository

    def run(self, step: StepDeclaration, domain: str) -> StepExecutionResult:
        resolved_input = self.input_resolver.resolve(step, domain)
        execution = self.step_executor.execute(step, resolved_input.records)

        output_path = self.checkpoint_repository.save(
            step=step,
            domain=domain,
            input_path=resolved_input.source_path,
            input_records=resolved_input.records,
            execution=execution,
        )

        result = StepExecutionResult(
            step=step,
            domain=domain,
            input_path=str(resolved_input.source_path),
            output_path=str(output_path),
            input_records=len(resolved_input.records),
            output_records=len(execution.records),
            errors=execution.errors,
            duration_ms=execution.duration_ms,
        )
        self.audit_repository.append(
            AuditEntry(
                timestamp=datetime.now(tz=timezone.utc).isoformat(),
                step_id=step.step_id,
                layer=step.layer,
                domain=domain,
                input_path=result.input_path,
                output_path=result.output_path,
                input_records=result.input_records,
                output_records=result.output_records,
                errors=result.errors,
                duration_ms=result.duration_ms,
            ),
        )
        if execution.errors:
            msg = f"Błąd parsera kroku {step.step_id}: {execution.errors[0]}"
            raise RuntimeError(msg)
        return result
