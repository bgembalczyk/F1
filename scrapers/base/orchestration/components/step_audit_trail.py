import csv
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from scrapers.base.orchestration.models import AuditEntry


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
