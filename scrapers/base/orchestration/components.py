from __future__ import annotations

import csv
import json
import time
from dataclasses import asdict
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Any

from scrapers.base.orchestration.models import AuditEntry
from scrapers.base.orchestration.models import CheckpointMetadata
from scrapers.base.orchestration.models import CheckpointMetrics
from scrapers.base.orchestration.models import CheckpointPayload
from scrapers.base.orchestration.models import ExecutedStep
from scrapers.base.orchestration.models import ResolvedInput
from scrapers.base.orchestration.models import StepDeclaration
from scrapers.base.orchestration.models import _OrchestrationPaths


class SectionSourceAdapter:
    """Pobiera wejście dla kroku z checkpointów i fallbackiem do raw."""

    def __init__(self, base_dir: Path = Path("data")) -> None:
        self.paths = _OrchestrationPaths(base_dir=base_dir)

    def resolve(self, step: StepDeclaration, domain: str) -> ResolvedInput:
        resolved_path = self._resolve_source_path(step, domain)
        if resolved_path is None:
            msg = (
                "Brak źródła wejścia dla "
                f"kroku={step.step_id}, source={step.input_source}"
            )
            raise FileNotFoundError(msg)
        return ResolvedInput(
            records=self._read_records(resolved_path),
            source_path=resolved_path,
        )

    def _resolve_source_path(self, step: StepDeclaration, domain: str) -> Path | None:
        direct_path = Path(step.input_source)
        if direct_path.is_absolute() and direct_path.exists():
            return direct_path

        for resolver in (self._resolve_checkpoint, self._resolve_raw):
            resolved = resolver(step, domain)
            if resolved is not None:
                return resolved
        return None

    def _resolve_checkpoint(self, step: StepDeclaration, domain: str) -> Path | None:
        checkpoints_dir = self.paths.checkpoints
        explicit = checkpoints_dir / f"{step.input_source}.json"
        if explicit.exists():
            return explicit

        matches = sorted(checkpoints_dir.glob(f"*{step.input_source}*{domain}*.json"))
        if matches:
            return matches[-1]

        matches = sorted(checkpoints_dir.glob(f"step_*_{step.layer}_{domain}.json"))
        if matches:
            return matches[-1]
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

        matches = sorted(raw_dir.glob(f"**/*{domain}*.json"))
        if matches:
            return matches[-1]
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
    def execute(
        self,
        step: StepDeclaration,
        input_records: list[dict[str, Any]],
    ) -> ExecutedStep:
        started_at = time.perf_counter()
        errors: list[str] = []
        try:
            output_records = step.parser(input_records)
        except Exception as exc:
            output_records = []
            errors.append(str(exc))
        return ExecutedStep(
            records=output_records,
            errors=errors,
            duration_ms=(time.perf_counter() - started_at) * 1000,
        )


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
        output_path = self.paths.checkpoint_file(
            f"step_{step.step_id}_{step.layer}_{domain}.json",
        )
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


class StepAuditTrail:
    _CSV_FIELDS = [
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
    ]

    def __init__(self, json_path: Path, csv_path: Path) -> None:
        self.json_path = json_path
        self.csv_path = csv_path

    def append(self, entry: AuditEntry) -> None:
        self._append_json(entry)
        self._append_csv(entry)

    def _append_json(self, entry: AuditEntry) -> None:
        data = self._load_json()
        data.append(asdict(entry))
        self.json_path.parent.mkdir(parents=True, exist_ok=True)
        self.json_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _append_csv(self, entry: AuditEntry) -> None:
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)
        write_header = not self.csv_path.exists()
        with self.csv_path.open("a", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=self._CSV_FIELDS)
            if write_header:
                writer.writeheader()
            row = asdict(entry)
            row["errors"] = " | ".join(entry.errors)
            writer.writerow(row)

    def write_regression_report(self, report_path: Path) -> Path:
        entries = self._load_json()
        lines = self._build_regression_lines(entries)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return report_path

    def _build_regression_lines(self, entries: list[dict[str, Any]]) -> list[str]:
        totals = self._aggregate_totals(entries)
        grouped = self._aggregate_grouped(entries)
        lines = [
            "# Step Regression Audit Report",
            "",
            f"- Total runs: {totals['steps']}",
            f"- Total error runs: {totals['errors']}",
            f"- Total duration [ms]: {totals['duration_ms']:.3f}",
            "",
            "| step_id | layer | domain | runs | input_records | "
            "output_records | error_runs | duration_ms |",
            "|---:|---|---|---:|---:|---:|---:|---:|",
        ]
        for (step_id, layer, domain), data in sorted(grouped.items()):
            lines.append(
                "| "
                f"{step_id} | {layer} | {domain} | {data['runs']} | "
                f"{data['input_records']} | {data['output_records']} | "
                f"{data['errors']} | {data['duration_ms']:.3f} |",
            )
        return lines

    @staticmethod
    def _aggregate_totals(entries: list[dict[str, Any]]) -> dict[str, float | int]:
        return {
            "steps": len(entries),
            "errors": sum(1 for entry in entries if entry.get("errors")),
            "duration_ms": sum(
                float(entry.get("duration_ms", 0.0)) for entry in entries
            ),
        }

    @staticmethod
    def _aggregate_grouped(
        entries: list[dict[str, Any]],
    ) -> dict[tuple[int, str, str], dict[str, Any]]:
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
        return grouped

    def _load_json(self) -> list[dict[str, Any]]:
        if not self.json_path.exists():
            return []
        payload = json.loads(self.json_path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            return []
        return payload
