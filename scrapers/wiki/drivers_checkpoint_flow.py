from __future__ import annotations

import csv
import json
from dataclasses import asdict
from datetime import timezone
from datetime import datetime
from pathlib import Path
from time import perf_counter
from typing import Any
from typing import Callable

from scrapers.base.orchestration.lifecycle import STAGE_EXPORT
from scrapers.base.orchestration.lifecycle import STAGE_INGEST
from scrapers.base.orchestration.lifecycle import STAGE_MERGE
from scrapers.base.orchestration.lifecycle import STAGE_NORMALIZE
from scrapers.base.orchestration.lifecycle import STAGE_VALIDATE
from scrapers.base.orchestration.lifecycle import StageCheckpointDumper
from scrapers.base.orchestration.lifecycle import StageEnvelope
from scrapers.base.orchestration.models import AuditEntry


class DriversCheckpointFlow:
    def __init__(
        self,
        *,
        source_file: Path,
        checkpoint_file: Path,
        layer1_output_file: Path,
        registry_file: Path,
        detail_fetcher: Callable[[str], dict[str, Any]] | None = None,
        checkpoint_dump_domains: set[str] | None = None,
    ) -> None:
        self._source_file = source_file
        self._checkpoint_file = checkpoint_file
        self._layer1_output_file = layer1_output_file
        self._registry_file = registry_file
        self._detail_fetcher = detail_fetcher or (lambda url: {"url": url})
        self._dumper = StageCheckpointDumper(
            checkpoints_dir=checkpoint_file.parent,
            enabled_domains=checkpoint_dump_domains or set(),
        )

    def run_layer0_checkpoint(self) -> None:
        raw_records = self._read_records(self._source_file)
        started = perf_counter()

        ingest_payload = StageEnvelope(
            domain="drivers",
            stage=STAGE_INGEST,
            records=raw_records,
            metadata={"input_source": str(self._source_file)},
        )
        self._dumper.dump(ingest_payload)

        normalized = [self._normalize_seed_row(row) for row in ingest_payload.records]
        normalize_payload = StageEnvelope(
            domain="drivers",
            stage=STAGE_NORMALIZE,
            records=[row for row in normalized if row],
            metadata=ingest_payload.metadata,
        )
        self._dumper.dump(normalize_payload)

        merged_payload = StageEnvelope(
            domain="drivers",
            stage=STAGE_MERGE,
            records=self._deduplicate_by_url(normalize_payload.records),
            metadata=normalize_payload.metadata,
        )
        self._dumper.dump(merged_payload)

        validate_payload = StageEnvelope(
            domain="drivers",
            stage=STAGE_VALIDATE,
            records=[row for row in merged_payload.records if row.get("url")],
            metadata=merged_payload.metadata,
        )
        self._dumper.dump(validate_payload)

        duration_ms = (perf_counter() - started) * 1000.0
        self._write_checkpoint(
            path=self._checkpoint_file,
            step_id=0,
            layer="layer0",
            parser="_parse_layer0_urls",
            input_source=str(self._source_file),
            output_target="checkpoints",
            records=validate_payload.records,
            duration_ms=duration_ms,
            input_records=len(raw_records),
        )

        self._append_audit(
            AuditEntry(
                timestamp=self._timestamp(),
                step_id=0,
                layer="layer0",
                domain="drivers",
                input_path=str(self._source_file),
                output_path=str(self._checkpoint_file),
                input_records=len(raw_records),
                output_records=len(validate_payload.records),
                errors=[],
                duration_ms=duration_ms,
            ),
        )

    def run_layer1_from_checkpoint(self) -> None:
        checkpoint_records = self._read_records(self._checkpoint_file)
        output_payload = self._read_checkpoint_payload(self._layer1_output_file)
        existing_urls = {row.get("url") for row in output_payload.get("records", [])}
        started = perf_counter()

        ingest_payload = StageEnvelope(
            domain="drivers",
            stage=STAGE_INGEST,
            records=checkpoint_records,
            metadata={"input_source": str(self._checkpoint_file)},
        )
        self._dumper.dump(ingest_payload)

        normalize_payload = StageEnvelope(
            domain="drivers",
            stage=STAGE_NORMALIZE,
            records=[self._normalize_seed_row(row) for row in ingest_payload.records],
            metadata=ingest_payload.metadata,
        )
        self._dumper.dump(normalize_payload)

        merge_payload = StageEnvelope(
            domain="drivers",
            stage=STAGE_MERGE,
            records=[
                row
                for row in self._deduplicate_by_url(normalize_payload.records)
                if row.get("url") and row.get("url") not in existing_urls
            ],
            metadata=normalize_payload.metadata,
        )
        self._dumper.dump(merge_payload)

        validate_payload = StageEnvelope(
            domain="drivers",
            stage=STAGE_VALIDATE,
            records=[row for row in merge_payload.records if isinstance(row.get("url"), str)],
            metadata=merge_payload.metadata,
        )
        self._dumper.dump(validate_payload)

        new_records: list[dict[str, Any]] = []
        for row in validate_payload.records:
            url = str(row.get("url", ""))
            if not url:
                continue
            details = self._detail_fetcher(url)
            new_records.append({"url": url, **details})

        final_records = output_payload.get("records", []) + new_records
        duration_ms = (perf_counter() - started) * 1000.0

        self._write_checkpoint(
            path=self._layer1_output_file,
            step_id=1,
            layer="layer1",
            parser="_parse_layer1_details",
            input_source=str(self._checkpoint_file),
            output_target="checkpoints",
            records=final_records,
            duration_ms=duration_ms,
            input_records=len(checkpoint_records),
        )

        self._dumper.dump(
            StageEnvelope(
                domain="drivers",
                stage=STAGE_EXPORT,
                records=final_records,
                metadata={"output_target": str(self._layer1_output_file)},
            ),
        )

        self._append_audit(
            AuditEntry(
                timestamp=self._timestamp(),
                step_id=1,
                layer="layer1",
                domain="drivers",
                input_path=str(self._checkpoint_file),
                output_path=str(self._layer1_output_file),
                input_records=len(checkpoint_records),
                output_records=len(final_records),
                errors=[],
                duration_ms=duration_ms,
            ),
        )

    def _append_audit(self, entry: AuditEntry) -> None:
        self._registry_file.parent.mkdir(parents=True, exist_ok=True)
        registry_payload = self._read_json_payload(self._registry_file)
        runs = registry_payload.get("runs", []) if isinstance(registry_payload, dict) else []
        runs.append(asdict(entry))
        self._registry_file.write_text(
            json.dumps({"runs": runs}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        audit_json = self._checkpoint_file.parent / "step_audit.json"
        existing = self._read_json_payload(audit_json)
        entries = existing if isinstance(existing, list) else []
        entries.append(asdict(entry))
        audit_json.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")

        csv_file = self._checkpoint_file.parent / "step_audit.csv"
        fieldnames = [
            "timestamp",
            "step_id",
            "layer",
            "domain",
            "input_path",
            "output_path",
            "input_records",
            "output_records",
            "duration_ms",
        ]
        with csv_file.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for row in entries:
                writer.writerow({key: row.get(key) for key in fieldnames})

    def _write_checkpoint(
        self,
        *,
        path: Path,
        step_id: int,
        layer: str,
        parser: str,
        input_source: str,
        output_target: str,
        records: list[dict[str, Any]],
        duration_ms: float,
        input_records: int,
    ) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "metadata": {
                "step_id": step_id,
                "layer": layer,
                "domain": "drivers",
                "input_source": input_source,
                "output_target": output_target,
                "parser": parser,
                "generated_at": self._timestamp(),
                "metrics": {
                    "input_records": input_records,
                    "output_records": len(records),
                    "errors": 0,
                    "duration_ms": duration_ms,
                    "input_path": input_source,
                },
            },
            "records": records,
        }
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    @staticmethod
    def _read_checkpoint_payload(path: Path) -> dict[str, Any]:
        payload = DriversCheckpointFlow._read_json_payload(path)
        return payload if isinstance(payload, dict) else {"records": []}

    @staticmethod
    def _read_json_payload(path: Path) -> Any:
        if not path.exists():
            return {} if path.suffix == ".json" else None
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _read_records(path: Path) -> list[dict[str, Any]]:
        payload = DriversCheckpointFlow._read_json_payload(path)
        if isinstance(payload, list):
            return [row for row in payload if isinstance(row, dict)]
        if isinstance(payload, dict):
            records = payload.get("records", [])
            if isinstance(records, list):
                return [row for row in records if isinstance(row, dict)]
        return []

    @staticmethod
    def _normalize_seed_row(row: dict[str, Any]) -> dict[str, Any]:
        if "url" in row:
            return {"name": str(row.get("name", "")), "url": str(row.get("url", ""))}
        driver = row.get("driver", {})
        if isinstance(driver, dict):
            return {
                "name": str(driver.get("text", "")),
                "url": str(driver.get("url", "")),
            }
        return {"name": "", "url": ""}

    @staticmethod
    def _deduplicate_by_url(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        seen: set[str] = set()
        normalized: list[dict[str, Any]] = []
        for record in records:
            url = str(record.get("url", "")).strip()
            if not url or url in seen:
                continue
            seen.add(url)
            normalized.append({"name": str(record.get("name", "")), "url": url})
        return normalized

    @staticmethod
    def _timestamp() -> str:
        return datetime.now(timezone.utc).isoformat()
