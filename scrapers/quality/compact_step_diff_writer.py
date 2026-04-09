import json
from pathlib import Path
from typing import Any
from typing import Mapping

from scrapers.quality.reporter import QualityReporter


class CompactStepDiffWriter:
    """Writes compact before/after diffs between consecutive pipeline steps."""

    def __init__(
        self,
        *,
        debug_dir: Path,
        run_id: str,
        domain_filter: set[str] | None = None,
        record_id_filter: set[str] | None = None,
    ) -> None:
        self._debug_dir = debug_dir
        self._run_id = run_id
        self._domain_filter = (
            {domain.strip().lower() for domain in domain_filter if domain.strip()}
            if domain_filter
            else None
        )
        self._record_id_filter = (
            {record_id.strip() for record_id in record_id_filter if record_id.strip()}
            if record_id_filter
            else None
        )
        self._previous_step_name: str | None = None
        self._previous_records: list[dict[str, Any]] = []

    def set_run_id(self, run_id: str) -> None:
        self._run_id = run_id

    def write_step_diff(
        self,
        *,
        step_name: str,
        records: list[dict[str, Any]],
        source_metadata: Mapping[str, Any],
    ) -> Path | None:
        domain = str(source_metadata.get("domain") or "").strip()
        if (
            self._domain_filter is not None
            and domain.lower() not in self._domain_filter
        ):
            self._previous_records = list(records)
            self._previous_step_name = step_name
            return None

        before_by_id = self._index_records(self._previous_records, source_metadata)
        after_by_id = self._index_records(records, source_metadata)
        changed_entries: list[dict[str, Any]] = []

        all_record_ids = sorted(set(before_by_id) | set(after_by_id))
        for record_id in all_record_ids:
            if (
                self._record_id_filter is not None
                and record_id not in self._record_id_filter
            ):
                continue
            before_record = before_by_id.get(record_id)
            after_record = after_by_id.get(record_id)
            field_changes = self._compact_field_diff(before_record, after_record)
            if not field_changes:
                continue
            changed_entries.append(
                {
                    "stage": step_name,
                    "previous_stage": self._previous_step_name,
                    "domain": domain,
                    "source": str(
                        source_metadata.get("url")
                        or source_metadata.get("scraper")
                        or "unknown",
                    ),
                    "record_id": record_id,
                    "changed_fields": field_changes,
                },
            )

        self._previous_records = list(records)
        self._previous_step_name = step_name
        if not changed_entries:
            return None

        output_path = self._debug_dir / f"debug_step_diffs_{self._run_id}.jsonl"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("a", encoding="utf-8") as handle:
            for entry in changed_entries:
                handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return output_path

    @staticmethod
    def _compact_field_diff(
        before_record: dict[str, Any] | None,
        after_record: dict[str, Any] | None,
    ) -> dict[str, dict[str, Any]]:
        before = before_record or {}
        after = after_record or {}
        changed: dict[str, dict[str, Any]] = {}
        for field in sorted(set(before) | set(after)):
            before_value = before.get(field)
            after_value = after.get(field)
            if before_value == after_value:
                continue
            changed[field] = {"before": before_value, "after": after_value}
        return changed

    @staticmethod
    def _index_records(
        records: list[dict[str, Any]],
        source_metadata: Mapping[str, Any],
    ) -> dict[str, dict[str, Any]]:
        key_fields = QualityReporter.normalize_primary_key(
            source_metadata.get("primary_key"),
        )
        if not key_fields and records and "url" in records[0]:
            key_fields = ["url"]

        indexed: dict[str, dict[str, Any]] = {}
        for index, record in enumerate(records):
            record_id = CompactStepDiffWriter._resolve_record_id(
                record=record,
                index=index,
                key_fields=key_fields,
            )
            indexed[record_id] = record
        return indexed

    @staticmethod
    def _resolve_record_id(
        *,
        record: Mapping[str, Any],
        index: int,
        key_fields: list[str],
    ) -> str:
        if key_fields:
            joined = QualityReporter.join_key_fields(record, key_fields)
            if joined:
                return joined
        if isinstance(record.get("id"), str) and record["id"]:
            return record["id"]
        if isinstance(record.get("name"), str) and record["name"]:
            return str(record["name"])
        return f"idx:{index}"
