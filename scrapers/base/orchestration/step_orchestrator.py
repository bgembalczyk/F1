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

from scrapers.data_paths import DataPaths
from scrapers.data_paths import DomainId

if TYPE_CHECKING:
    from collections.abc import Callable




@dataclass(frozen=True)
class StepDeclaration:
    step_id: int
    layer: str
    input_source: str
    parser: Callable[[list[dict[str, Any]]], list[dict[str, Any]]]
    output_target: str


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


class SectionSourceAdapter:
    """Pobiera wejście dla kroku z checkpointów i fallbackiem do raw."""

    def __init__(self, base_dir: Path = Path("data")) -> None:
        self.base_dir = base_dir
        self.paths = DataPaths(base_dir=base_dir)

    def resolve(
        self,
        step: StepDeclaration,
        domain: str,
    ) -> tuple[list[dict[str, Any]], Path]:
        direct_path = Path(step.input_source)
        if direct_path.is_absolute() and direct_path.exists():
            return self._read_records(direct_path), direct_path

        checkpoint_path = self._resolve_checkpoint(step, domain)
        if checkpoint_path is not None:
            return self._read_records(checkpoint_path), checkpoint_path

        raw_path = self._resolve_raw(step, domain)
        if raw_path is not None:
            return self._read_records(raw_path), raw_path

        msg = (
            "Brak źródła wejścia dla "
            f"kroku={step.step_id}, source={step.input_source}"
        )
        raise FileNotFoundError(msg)

    def _resolve_checkpoint(self, step: StepDeclaration, domain: str) -> Path | None:
        checkpoints_dir = self.paths.checkpoints
        explicit = self.paths.checkpoint_file(f"{step.input_source}.json")
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
                f"step_*_{step.layer}_{DomainId(domain)}.json",
            ),
        )
        if layer_match:
            return layer_match[-1]
        return None

    def _resolve_raw(self, step: StepDeclaration, domain: str) -> Path | None:
        raw_dir = self.paths.raw
        candidates = [
            raw_dir / f"{step.input_source}.json",
            self.paths.raw_file(domain, f"{step.input_source}.json"),
            self.paths.raw_file(domain, f"{DomainId(domain)}.json"),
            self.paths.legacy_wiki_file(domain, f"{step.input_source}.json"),
            self.paths.legacy_wiki_file(domain, f"{DomainId(domain)}.json"),
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate

        wildcard = sorted(raw_dir.glob(f"**/*{DomainId(domain)}*.json"))
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
        source_adapter: SectionSourceAdapter | None = None,
        audit_trail: StepAuditTrail | None = None,
    ) -> None:
        self.base_dir = base_dir
        self.paths = DataPaths(base_dir=base_dir)
        self.source_adapter = source_adapter or SectionSourceAdapter(base_dir=base_dir)
        self.audit_trail = audit_trail or StepAuditTrail(
            json_path=self.paths.audit_file("step_audit.json"),
            csv_path=self.paths.audit_file("step_audit.csv"),
        )

    def run(self, step: StepDeclaration, domain: str) -> StepExecutionResult:
        input_records, input_path = self.source_adapter.resolve(step, domain)
        errors: list[str] = []
        started_at = time.perf_counter()

        try:
            output_records = step.parser(input_records)
        except Exception as exc:  # noqa: BLE001
            output_records = []
            errors.append(str(exc))

        output_path = self._output_path(step, domain)
        duration_ms = (time.perf_counter() - started_at) * 1000
        payload = {
            "metadata": {
                "step_id": step.step_id,
                "layer": step.layer,
                "domain": domain,
                "input_source": str(input_path),
                "output_target": step.output_target,
                "parser": step.parser.__name__,
                "generated_at": datetime.now(tz=timezone.utc).isoformat(),
                "metrics": {
                    "input_records": len(input_records),
                    "output_records": len(output_records),
                    "errors": len(errors),
                    "duration_ms": duration_ms,
                    "input_path": str(input_path),
                },
            },
            "records": output_records,
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        result = StepExecutionResult(
            step=step,
            domain=domain,
            input_path=str(input_path),
            output_path=str(output_path),
            input_records=len(input_records),
            output_records=len(output_records),
            errors=errors,
            duration_ms=duration_ms,
        )
        self.audit_trail.append(
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
        if errors:
            msg = f"Błąd parsera kroku {step.step_id}: {errors[0]}"
            raise RuntimeError(msg)
        return result

    def _output_path(self, step: StepDeclaration, domain: str) -> Path:
        return self.paths.checkpoint_step_file(step.step_id, step.layer, domain)
