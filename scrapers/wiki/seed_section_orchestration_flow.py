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

from scrapers.base.orchestration.components.section_source_adapter import SectionSourceAdapter
from scrapers.base.orchestration.lifecycle import STAGE_EXPORT
from scrapers.base.orchestration.lifecycle import STAGE_INGEST
from scrapers.base.orchestration.lifecycle import STAGE_MERGE
from scrapers.base.orchestration.lifecycle import STAGE_NORMALIZE
from scrapers.base.orchestration.lifecycle import STAGE_VALIDATE
from scrapers.base.orchestration.lifecycle import StageCheckpointDumper
from scrapers.base.orchestration.lifecycle import StageEnvelope
from scrapers.base.orchestration.models import AuditEntry
from scrapers.base.orchestration.models import StepDeclaration

SUPPORTED_DOMAINS: tuple[str, ...] = (
    "drivers",
    "constructors",
    "circuits",
    "seasons",
    "grands_prix",
)


class SeedSectionOrchestrationFlow:
    def __init__(
        self,
        *,
        base_dir: Path,
        detail_fetchers: dict[str, Callable[[str], dict[str, Any]]],
        checkpoint_dump_domains: set[str] | None = None,
    ) -> None:
        self._base_dir = base_dir
        self._detail_fetchers = detail_fetchers
        self._source_adapter = SectionSourceAdapter(base_dir=base_dir)
        self._checkpoints_dir = base_dir / "checkpoints"
        self._dumper = StageCheckpointDumper(
            checkpoints_dir=self._checkpoints_dir,
            enabled_domains=checkpoint_dump_domains or set(),
        )

    def run(self, domains: tuple[str, ...] = SUPPORTED_DOMAINS) -> dict[str, str]:
        outputs: dict[str, str] = {}
        audit_entries: list[AuditEntry] = []

        for domain in domains:
            fetcher = self._detail_fetchers.get(domain)
            if fetcher is None:
                continue

            l0_records, l0_audit = self._run_layer0(domain)
            self._write_checkpoint(
                step_id=0,
                layer="layer0",
                domain=domain,
                parser="_parse_layer0_seed",
                input_source=l0_audit.input_path,
                output_target="checkpoints",
                records=l0_records,
                duration_ms=l0_audit.duration_ms,
                input_records=l0_audit.input_records,
            )
            audit_entries.append(l0_audit)

            l1_records, l1_audit = self._run_layer1(domain, fetcher)
            l1_path = self._write_checkpoint(
                step_id=1,
                layer="layer1",
                domain=domain,
                parser="_parse_layer1_details",
                input_source=l1_audit.input_path,
                output_target="checkpoints",
                records=l1_records,
                duration_ms=l1_audit.duration_ms,
                input_records=l1_audit.input_records,
            )
            outputs[domain] = str(l1_path)
            audit_entries.append(l1_audit)
            self._dumper.dump(
                StageEnvelope(
                    domain=domain,
                    stage=STAGE_EXPORT,
                    records=l1_records,
                    metadata={"output_target": str(l1_path)},
                ),
            )

        report_path = self._write_audit(audit_entries)
        outputs["report"] = str(report_path)
        return outputs

    def _run_layer0(self, domain: str) -> tuple[list[dict[str, Any]], AuditEntry]:
        step = StepDeclaration(
            step_id=0,
            layer="layer0",
            input_source=domain,
            parser=lambda rows: rows,
            output_target="checkpoints",
        )
        resolved = self._source_adapter.resolve(step, domain)
        started = perf_counter()

        ingest_payload = StageEnvelope(
            domain=domain,
            stage=STAGE_INGEST,
            records=resolved.records,
            metadata={"input_source": str(resolved.source_path)},
        )
        self._dumper.dump(ingest_payload)

        normalized = [self._normalize_seed_row(domain, row) for row in ingest_payload.records]
        normalize_payload = StageEnvelope(
            domain=domain,
            stage=STAGE_NORMALIZE,
            records=[row for row in normalized if row.get("url")],
            metadata=ingest_payload.metadata,
        )
        self._dumper.dump(normalize_payload)

        merged_payload = StageEnvelope(
            domain=domain,
            stage=STAGE_MERGE,
            records=self._deduplicate_by_url(normalize_payload.records),
            metadata=normalize_payload.metadata,
        )
        self._dumper.dump(merged_payload)

        validate_payload = StageEnvelope(
            domain=domain,
            stage=STAGE_VALIDATE,
            records=[row for row in merged_payload.records if row.get("url")],
            metadata=merged_payload.metadata,
        )
        self._dumper.dump(validate_payload)

        duration_ms = (perf_counter() - started) * 1000.0
        audit = AuditEntry(
            timestamp=self._timestamp(),
            step_id=0,
            layer="layer0",
            domain=domain,
            input_path=str(resolved.source_path),
            output_path=str(self._checkpoint_path(0, "layer0", domain)),
            input_records=len(resolved.records),
            output_records=len(validate_payload.records),
            errors=[],
            duration_ms=duration_ms,
        )
        return validate_payload.records, audit

    def _run_layer1(
        self,
        domain: str,
        fetcher: Callable[[str], dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], AuditEntry]:
        step = StepDeclaration(
            step_id=1,
            layer="layer1",
            input_source=f"step_0_layer0_{domain}",
            parser=lambda rows: rows,
            output_target="checkpoints",
        )
        resolved = self._source_adapter.resolve(step, domain)
        started = perf_counter()

        ingest_payload = StageEnvelope(
            domain=domain,
            stage=STAGE_INGEST,
            records=resolved.records,
            metadata={"input_source": str(resolved.source_path)},
        )
        self._dumper.dump(ingest_payload)

        normalize_payload = StageEnvelope(
            domain=domain,
            stage=STAGE_NORMALIZE,
            records=[self._normalize_seed_row(domain, row) for row in ingest_payload.records],
            metadata=ingest_payload.metadata,
        )
        self._dumper.dump(normalize_payload)

        merge_payload = StageEnvelope(
            domain=domain,
            stage=STAGE_MERGE,
            records=self._deduplicate_by_url(normalize_payload.records),
            metadata=normalize_payload.metadata,
        )
        self._dumper.dump(merge_payload)

        layer1_records = [
            {"url": str(record.get("url", "")), "details": fetcher(str(record.get("url", "")))}
            for record in merge_payload.records
            if record.get("url")
        ]

        validate_payload = StageEnvelope(
            domain=domain,
            stage=STAGE_VALIDATE,
            records=[record for record in layer1_records if record.get("url")],
            metadata=merge_payload.metadata,
        )
        self._dumper.dump(validate_payload)

        duration_ms = (perf_counter() - started) * 1000.0
        audit = AuditEntry(
            timestamp=self._timestamp(),
            step_id=1,
            layer="layer1",
            domain=domain,
            input_path=str(resolved.source_path),
            output_path=str(self._checkpoint_path(1, "layer1", domain)),
            input_records=len(resolved.records),
            output_records=len(validate_payload.records),
            errors=[],
            duration_ms=duration_ms,
        )
        return validate_payload.records, audit

    def _write_checkpoint(
        self,
        *,
        step_id: int,
        layer: str,
        domain: str,
        parser: str,
        input_source: str,
        output_target: str,
        records: list[dict[str, Any]],
        duration_ms: float,
        input_records: int,
    ) -> Path:
        path = self._checkpoint_path(step_id, layer, domain)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "metadata": {
                "step_id": step_id,
                "layer": layer,
                "domain": domain,
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
        return path

    def _write_audit(self, entries: list[AuditEntry]) -> Path:
        self._checkpoints_dir.mkdir(parents=True, exist_ok=True)
        audit_json = self._checkpoints_dir / "step_audit.json"
        audit_json.write_text(
            json.dumps([asdict(entry) for entry in entries], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        audit_csv = self._checkpoints_dir / "step_audit.csv"
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
        with audit_csv.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for entry in entries:
                writer.writerow({name: getattr(entry, name) for name in fieldnames})

        report_path = self._checkpoints_dir / "step_regression_report.md"
        lines = [
            "# Step Regression Audit Report",
            "",
            "| step_id | layer | domain | input_records | output_records | duration_ms |",
            "|---|---|---|---:|---:|---:|",
        ]
        for entry in entries:
            lines.append(
                f"| {entry.step_id} | {entry.layer} | {entry.domain} "
                f"| {entry.input_records} | {entry.output_records} | {entry.duration_ms:.2f} |",
            )
        report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return report_path

    def _checkpoint_path(self, step_id: int, layer: str, domain: str) -> Path:
        return self._checkpoints_dir / f"step_{step_id}_{layer}_{domain}.json"

    @staticmethod
    def _normalize_seed_row(domain: str, row: dict[str, Any]) -> dict[str, Any]:
        if "url" in row:
            return {"name": str(row.get("name", "")), "url": str(row.get("url", ""))}

        key_map = {
            "drivers": "driver",
            "constructors": "constructor",
            "circuits": "circuit",
            "seasons": "season",
            "grands_prix": "grand_prix",
        }
        domain_key = key_map.get(domain, "")
        nested = row.get(domain_key)
        if isinstance(nested, dict):
            return {
                "name": str(nested.get("text", "")),
                "url": str(nested.get("url", "")),
            }
        return {"name": "", "url": ""}

    @staticmethod
    def _deduplicate_by_url(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        seen: set[str] = set()
        normalized: list[dict[str, Any]] = []
        for row in records:
            url = str(row.get("url", "")).strip()
            if not url or url in seen:
                continue
            seen.add(url)
            normalized.append({"name": str(row.get("name", "")), "url": url})
        return normalized

    @staticmethod
    def _timestamp() -> str:
        return datetime.now(timezone.utc).isoformat()
