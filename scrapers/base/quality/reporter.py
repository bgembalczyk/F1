from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0"


@dataclass(slots=True)
class QualityReporter:
    """Generuje raport jakości dla kolejnych kroków pipeline scrapera."""

    report_root: Path
    run_id: str
    source_metadata: Mapping[str, Any]
    schema_version: str = SCHEMA_VERSION

    def report_step(
        self,
        *,
        step_id: str,
        records: list[dict[str, Any]] | None,
        source_metadata: Mapping[str, Any] | None = None,
    ) -> Path:
        resolved_records = records or []
        payload = {
            "step_id": step_id,
            "schema_version": self.schema_version,
            "record_count": len(resolved_records),
            "null_rate": self._null_rate(resolved_records),
            "missing_fields": self._missing_fields(resolved_records),
            "duplicate_keys": self._duplicate_keys(
                resolved_records,
                source_metadata=source_metadata,
            ),
            "duplicate_logical_key_count": self._duplicate_logical_key_count(
                resolved_records,
                source_metadata=source_metadata,
            ),
            "source_metadata": dict(source_metadata or self.source_metadata),
            "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        }

        output_path = self.report_root / f"quality_report_step_{step_id}.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return output_path

    @staticmethod
    def _missing_fields(records: list[dict[str, Any]]) -> dict[str, int]:
        all_fields: set[str] = set()
        for record in records:
            all_fields.update(record.keys())

        counts: dict[str, int] = {}
        for field in sorted(all_fields):
            missing_count = sum(
                1
                for record in records
                if field not in record or record.get(field) in (None, "")
            )
            if missing_count:
                counts[field] = missing_count
        return counts

    def _duplicate_keys(
        self,
        records: list[dict[str, Any]],
        *,
        source_metadata: Mapping[str, Any] | None,
    ) -> dict[str, int]:
        metadata = source_metadata or self.source_metadata
        configured_primary_key = metadata.get("primary_key")
        key_fields = self._normalize_primary_key(configured_primary_key)

        if not key_fields and records and "url" in records[0]:
            key_fields = ["url"]

        if key_fields:
            keys: list[str] = []
            for record in records:
                joined = self._join_key_fields(record, key_fields)
                if joined is not None:
                    keys.append(joined)
        else:
            keys = [
                json.dumps(record, ensure_ascii=False, sort_keys=True)
                for record in records
            ]

        return {key: count for key, count in sorted(Counter(keys).items()) if count > 1}

    def _duplicate_logical_key_count(
        self,
        records: list[dict[str, Any]],
        *,
        source_metadata: Mapping[str, Any] | None,
    ) -> int:
        return sum(
            count - 1
            for count in self._duplicate_keys(
                records,
                source_metadata=source_metadata,
            ).values()
        )

    @staticmethod
    def _null_rate(records: list[dict[str, Any]]) -> float:
        if not records:
            return 0.0
        all_fields: set[str] = set()
        for record in records:
            all_fields.update(record.keys())

        if not all_fields:
            return 0.0

        total_cells = len(records) * len(all_fields)
        null_cells = 0
        for record in records:
            for field in all_fields:
                if field not in record or record.get(field) in (None, ""):
                    null_cells += 1
        return round(null_cells / total_cells, 6)

    @staticmethod
    def _normalize_primary_key(value: Any) -> list[str]:
        if isinstance(value, str) and value:
            return [value]
        if isinstance(value, (list, tuple)):
            return [str(item) for item in value if item]
        return []

    @staticmethod
    def _join_key_fields(
        record: Mapping[str, Any],
        key_fields: list[str],
    ) -> str | None:
        values: list[str] = []
        for field in key_fields:
            value = record.get(field)
            if value in (None, ""):
                return None
            values.append(str(value))
        return "::".join(values)
