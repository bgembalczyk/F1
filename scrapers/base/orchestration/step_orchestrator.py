from __future__ import annotations

import csv
import json
from dataclasses import asdict
from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any

if TYPE_CHECKING:
    from collections.abc import Callable

from scrapers.config import DataPaths
from scrapers.config import default_data_paths


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


class SectionSourceAdapter:
    """Pobiera wejście dla kroku z checkpointów i fallbackiem do raw."""

    def __init__(self, base_dir: Path = Path("data")) -> None:
        self.base_dir = base_dir
        self.paths = default_data_paths(base_dir=base_dir)

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
                ],
            )
            if write_header:
                writer.writeheader()
            row = asdict(entry)
            row["errors"] = " | ".join(entry.errors)
            writer.writerow(row)

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
        self.paths: DataPaths = default_data_paths(base_dir=base_dir)
        self.source_adapter = source_adapter or SectionSourceAdapter(base_dir=base_dir)
        self.audit_trail = audit_trail or StepAuditTrail(
            json_path=self.paths.checkpoint_file("step_audit.json"),
            csv_path=self.paths.checkpoint_file("step_audit.csv"),
        )

    def run(self, step: StepDeclaration, domain: str) -> StepExecutionResult:
        input_records, input_path = self.source_adapter.resolve(step, domain)
        errors: list[str] = []

        try:
            output_records = step.parser(input_records)
        except Exception as exc:  # noqa: BLE001
            output_records = []
            errors.append(str(exc))

        output_path = self._output_path(step, domain)
        payload = {
            "metadata": {
                "step_id": step.step_id,
                "layer": step.layer,
                "domain": domain,
                "input_source": str(input_path),
                "output_target": step.output_target,
                "parser": step.parser.__name__,
                "generated_at": datetime.now(tz=timezone.utc).isoformat(),
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
            ),
        )
        if errors:
            msg = f"Błąd parsera kroku {step.step_id}: {errors[0]}"
            raise RuntimeError(msg)
        return result

    def _output_path(self, step: StepDeclaration, domain: str) -> Path:
        name = f"step_{step.step_id}_{step.layer}_{domain}.json"
        return self.paths.checkpoint_file(name)
