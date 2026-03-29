from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable


@dataclass
class DriversCheckpointFlow:
    source_file: Path
    checkpoint_file: Path
    layer1_output_file: Path
    registry_file: Path
    detail_fetcher: Callable[[str], dict[str, Any]] | None = None

    def _read_json(self, path: Path, default: Any) -> Any:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))

    def _write_json(self, path: Path, payload: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    def _append_audit(self, entry: dict[str, Any]) -> None:
        checkpoints_dir = self.checkpoint_file.parent
        json_path = checkpoints_dir / "step_audit.json"
        csv_path = checkpoints_dir / "step_audit.csv"

        audit = self._read_json(json_path, [])
        audit.append(entry)
        self._write_json(json_path, audit)

        rows = [(e.get("step_id"), e.get("layer"), e.get("domain")) for e in audit]
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        with csv_path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(["step_id", "layer", "domain"])
            writer.writerows(rows)

    def run_layer0_checkpoint(self) -> None:
        payload = self._read_json(self.source_file, [])
        records: list[dict[str, str]] = []
        for item in payload:
            driver = item.get("driver") if isinstance(item, dict) else None
            if isinstance(driver, dict):
                url = str(driver.get("url") or "")
                if url:
                    records.append({"name": str(driver.get("text") or ""), "url": url})

        checkpoint = {
            "metadata": {
                "input_source": str(self.source_file),
                "domain": "drivers",
                "parser": "_parse_layer0_urls",
            },
            "records": records,
        }
        self._write_json(self.checkpoint_file, checkpoint)

    def run_layer1_from_checkpoint(self) -> None:
        checkpoint = self._read_json(self.checkpoint_file, {"records": []})
        checkpoint_records = checkpoint.get("records", [])
        existing = self._read_json(self.layer1_output_file, {"records": []})
        done_urls = {str(item.get("url")) for item in existing.get("records", []) if isinstance(item, dict)}

        fetcher = self.detail_fetcher or (lambda url: {"url": url})
        output_records: list[dict[str, Any]] = list(existing.get("records", []))

        for item in checkpoint_records:
            if not isinstance(item, dict):
                continue
            url = str(item.get("url") or "")
            if not url or url in done_urls:
                continue
            details = fetcher(url)
            output_records.append({"url": url, **details})
            done_urls.add(url)

        self._write_json(self.layer1_output_file, {"records": output_records})

        self._append_audit(
            {
                "step_id": 1,
                "layer": "layer1",
                "domain": "drivers",
                "input_path": str(self.checkpoint_file),
                "output_path": str(self.layer1_output_file),
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
