from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Any


@dataclass
class DriversCheckpointFlow:
    source_file: Path
    checkpoint_file: Path
    layer1_output_file: Path
    registry_file: Path
    detail_fetcher: Any | None = None

    def __post_init__(self) -> None:
        if self.detail_fetcher is None:
            self.detail_fetcher = lambda url: {"url": url}

    def _read_json(self, path: Path, default: Any) -> Any:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))

    def _write_json(self, path: Path, payload: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    def _append_audit(self, *, step_id: int, layer: str, input_path: Path, output_path: Path, duration_ms: float) -> None:
        audit_path = self.checkpoint_file.parent / "step_audit.json"
        rows = self._read_json(audit_path, [])
        rows.append(
            {
                "step_id": step_id,
                "layer": layer,
                "domain": "drivers",
                "input_path": str(input_path),
                "output_path": str(output_path),
                "duration_ms": duration_ms,
            },
        )
        self._write_json(audit_path, rows)

        csv_path = self.checkpoint_file.parent / "step_audit.csv"
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        with csv_path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(
                fh,
                fieldnames=["step_id", "layer", "domain", "input_path", "output_path", "duration_ms"],
            )
            writer.writeheader()
            writer.writerows(rows)

    def _parse_layer0_urls(self, records: list[dict[str, Any]]) -> list[dict[str, str]]:
        parsed: list[dict[str, str]] = []
        for record in records:
            driver = record.get("driver", {})
            if isinstance(driver, dict):
                parsed.append({"name": str(driver.get("text") or ""), "url": str(driver.get("url") or "")})
        return parsed

    def run_layer0_checkpoint(self) -> None:
        start = perf_counter()
        payload = self._read_json(self.source_file, [])
        records = self._parse_layer0_urls(payload)
        self._write_json(
            self.checkpoint_file,
            {
                "metadata": {
                    "input_source": str(self.source_file),
                    "domain": "drivers",
                    "parser": "_parse_layer0_urls",
                },
                "records": records,
            },
        )
        self._append_audit(
            step_id=0,
            layer="layer0",
            input_path=self.source_file,
            output_path=self.checkpoint_file,
            duration_ms=(perf_counter() - start) * 1000,
        )

    def run_layer1_from_checkpoint(self) -> None:
        start = perf_counter()
        checkpoint = self._read_json(self.checkpoint_file, {"records": []})
        records = checkpoint.get("records", [])
        result_records = [self.detail_fetcher(record.get("url", "")) for record in records]
        self._write_json(self.layer1_output_file, {"records": result_records})
        self._append_audit(
            step_id=1,
            layer="layer1",
            input_path=self.checkpoint_file,
            output_path=self.layer1_output_file,
            duration_ms=(perf_counter() - start) * 1000,
        )
