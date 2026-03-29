from __future__ import annotations

import csv
import json
from dataclasses import asdict
from datetime import datetime
from datetime import timezone
from pathlib import Path
from time import perf_counter
from typing import Any

from scrapers.base.orchestration.models import AuditEntry
from scrapers.base.orchestration.models import CheckpointMetadata
from scrapers.base.orchestration.models import CheckpointMetrics
from scrapers.base.orchestration.models import CheckpointPayload
from scrapers.base.orchestration.models import StepExecutionResult


def _utcnow_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _read_json_records(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        rows = payload.get("records", [])
        if isinstance(rows, list):
            return [item for item in rows if isinstance(item, dict)]
    return []


def _extract_driver_row(record: dict[str, Any]) -> dict[str, Any]:
    name = ""
    url = None
    candidates = [record]
    for key in ("driver", "constructor", "circuit", "season", "grand_prix"):
        value = record.get(key)
        if isinstance(value, dict):
            candidates.append(value)

    for raw in candidates:
        maybe_name = raw.get("text") or raw.get("name")
        maybe_url = raw.get("url") or raw.get("link")
        if not name and maybe_name:
            name = str(maybe_name).strip()
        if not url and maybe_url:
            url = str(maybe_url).strip()
    return {"name": name, "url": url}


class DriversCheckpointFlow:
    def __init__(
        self,
        *,
        source_file: Path,
        checkpoint_file: Path,
        layer1_output_file: Path,
        registry_file: Path,
        detail_fetcher: Any | None = None,
    ) -> None:
        self._source_file = source_file
        self._checkpoint_file = checkpoint_file
        self._layer1_output_file = layer1_output_file
        self._registry_file = registry_file
        self._detail_fetcher = detail_fetcher or (lambda url: {"url": url})
        self._audit_json = checkpoint_file.parent / "step_audit.json"
        self._audit_csv = checkpoint_file.parent / "step_audit.csv"

    def run_layer0_checkpoint(self) -> StepExecutionResult:
        started = perf_counter()
        source_records = _read_json_records(self._source_file)
        parsed = [
            row
            for row in (_extract_driver_row(record) for record in source_records)
            if row.get("url")
        ]
        duration_ms = (perf_counter() - started) * 1000.0

        result = StepExecutionResult(
            status="parsed",
            records=parsed,
            errors=[],
            metrics={
                "input_records": len(source_records),
                "output_records": len(parsed),
                "errors": 0,
                "duration_ms": duration_ms,
            },
            output_paths={"source_path": str(self._source_file)},
        )
        self._save_checkpoint(
            output_path=self._checkpoint_file,
            result=result,
            step_id=0,
            layer="layer0",
            domain="drivers",
            parser_name="_parse_layer0_urls",
            input_source=str(self._source_file),
            output_target="checkpoints",
        )
        checkpointed = result.with_updates(
            status="checkpointed",
            output_paths={"checkpoint_path": str(self._checkpoint_file)},
        )
        self._append_audit(step_id=0, layer="layer0", domain="drivers", result=checkpointed)
        return checkpointed

    def run_layer1_from_checkpoint(self) -> StepExecutionResult:
        checkpoint_records = _read_json_records(self._checkpoint_file)
        output_payload = (
            json.loads(self._layer1_output_file.read_text(encoding="utf-8"))
            if self._layer1_output_file.exists()
            else {"records": []}
        )
        existing_records = output_payload.get("records", [])
        existing_urls = {
            rec.get("url")
            for rec in existing_records
            if isinstance(rec, dict) and isinstance(rec.get("url"), str)
        }

        errors: list[str] = []
        appended: list[dict[str, Any]] = []
        started = perf_counter()
        for record in checkpoint_records:
            url = record.get("url")
            if not isinstance(url, str) or not url or url in existing_urls:
                continue
            try:
                details = self._detail_fetcher(url)
                appended.append({"url": url, "details": details})
                existing_urls.add(url)
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{url}: {exc}")
        duration_ms = (perf_counter() - started) * 1000.0

        all_records = [*existing_records, *appended]
        result = StepExecutionResult(
            status="parsed",
            records=all_records,
            errors=errors,
            metrics={
                "input_records": len(checkpoint_records),
                "output_records": len(all_records),
                "errors": len(errors),
                "duration_ms": duration_ms,
            },
            output_paths={"source_path": str(self._checkpoint_file)},
        )

        self._save_checkpoint(
            output_path=self._layer1_output_file,
            result=result,
            step_id=1,
            layer="layer1",
            domain="drivers",
            parser_name="_fetch_driver_details",
            input_source=str(self._checkpoint_file),
            output_target="checkpoints",
        )
        self._append_audit(
            step_id=1,
            layer="layer1",
            domain="drivers",
            result=result.with_updates(
                status="audited",
                output_paths={"checkpoint_path": str(self._layer1_output_file)},
            ),
        )
        return result

    def _save_checkpoint(
        self,
        *,
        output_path: Path,
        result: StepExecutionResult,
        step_id: int,
        layer: str,
        domain: str,
        parser_name: str,
        input_source: str,
        output_target: str,
    ) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        metadata = CheckpointMetadata(
            step_id=step_id,
            layer=layer,
            domain=domain,
            input_source=input_source,
            output_target=output_target,
            parser=parser_name,
            generated_at=_utcnow_iso(),
            metrics=CheckpointMetrics(
                input_records=int(result.metrics.get("input_records", 0)),
                output_records=int(result.metrics.get("output_records", len(result.records))),
                errors=int(result.metrics.get("errors", len(result.errors))),
                duration_ms=float(result.metrics.get("duration_ms", 0.0)),
                input_path=result.output_paths.get("source_path", ""),
            ),
        )
        payload = CheckpointPayload(metadata=metadata, records=result.records)
        output_path.write_text(
            json.dumps(asdict(payload), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _append_audit(
        self,
        *,
        step_id: int,
        layer: str,
        domain: str,
        result: StepExecutionResult,
    ) -> None:
        entry = AuditEntry(
            timestamp=_utcnow_iso(),
            step_id=step_id,
            layer=layer,
            domain=domain,
            input_path=result.output_paths.get("source_path", ""),
            output_path=result.output_paths.get("checkpoint_path", ""),
            input_records=int(result.metrics.get("input_records", 0)),
            output_records=int(result.metrics.get("output_records", len(result.records))),
            errors=result.errors,
            duration_ms=float(result.metrics.get("duration_ms", 0.0)),
        )

        data: list[dict[str, Any]] = []
        if self._audit_json.exists():
            raw = json.loads(self._audit_json.read_text(encoding="utf-8"))
            if isinstance(raw, list):
                data = [item for item in raw if isinstance(item, dict)]
        data.append(asdict(entry))
        self._audit_json.parent.mkdir(parents=True, exist_ok=True)
        self._audit_json.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        with self._audit_csv.open("w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(
                csvfile,
                fieldnames=[
                    "step_id",
                    "layer",
                    "domain",
                    "input_path",
                    "output_path",
                    "input_records",
                    "output_records",
                    "duration_ms",
                    "errors",
                ],
            )
            writer.writeheader()
            for item in data:
                writer.writerow(
                    {
                        **{k: item.get(k, "") for k in writer.fieldnames},
                        "errors": " | ".join(item.get("errors", [])),
                    },
                )
