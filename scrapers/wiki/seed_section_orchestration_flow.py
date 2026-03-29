from __future__ import annotations

import json
from pathlib import Path
from time import perf_counter
from typing import Any


class SeedSectionOrchestrationFlow:
    DEFAULT_DOMAINS = ("drivers", "constructors", "circuits", "seasons", "grands_prix")

    def __init__(self, *, base_dir: Path, detail_fetchers: dict[str, Any]) -> None:
        self.base_dir = Path(base_dir)
        self.detail_fetchers = detail_fetchers
        self.checkpoints_dir = self.base_dir / "checkpoints"

    def _read_json(self, path: Path, default: Any) -> Any:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))

    def _write_json(self, path: Path, payload: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    def _source_path(self, domain: str) -> Path:
        return self.base_dir / "raw" / domain / f"{domain}.json"

    def _extract_url_name(self, item: dict[str, Any], domain: str) -> dict[str, str]:
        for key in (domain[:-1], "driver", "constructor", "circuit", "season", "grand_prix"):
            value = item.get(key)
            if isinstance(value, dict):
                return {"name": str(value.get("text") or ""), "url": str(value.get("url") or "")}
        return {"name": str(item.get("name") or ""), "url": str(item.get("url") or "")}

    def _load_l0_source_records(self, domain: str) -> list[dict[str, Any]]:
        checkpoint_fallback = self.checkpoints_dir / f"{domain}.json"
        if checkpoint_fallback.exists():
            payload = self._read_json(checkpoint_fallback, {"records": []})
            records = payload.get("records", [])
            if isinstance(records, list):
                return records
        return self._read_json(self._source_path(domain), [])

    def _run_l0(self, domain: str) -> tuple[Path, dict[str, Any]]:
        start = perf_counter()
        raw_records = self._load_l0_source_records(domain)
        records = [self._extract_url_name(item, domain) for item in raw_records if isinstance(item, dict)]
        duration_ms = (perf_counter() - start) * 1000
        payload = {
            "metadata": {"metrics": {"input_records": len(raw_records), "output_records": len(records), "errors": 0, "duration_ms": duration_ms}},
            "records": records,
        }
        out = self.checkpoints_dir / f"step_0_layer0_{domain}.json"
        self._write_json(out, payload)
        return out, payload

    def _run_l1(self, domain: str, l0_records: list[dict[str, Any]]) -> tuple[Path, dict[str, Any]]:
        start = perf_counter()
        fetcher = self.detail_fetchers[domain]
        records = []
        errors = 0
        for record in l0_records:
            url = str(record.get("url") or "")
            try:
                details = fetcher(url)
            except Exception:
                details = None
                errors += 1
            records.append({"url": url, "details": details})

        duration_ms = (perf_counter() - start) * 1000
        payload = {
            "metadata": {"metrics": {"input_records": len(l0_records), "output_records": len(records), "errors": errors, "duration_ms": duration_ms}},
            "records": records,
        }
        out = self.checkpoints_dir / f"step_1_layer1_{domain}.json"
        self._write_json(out, payload)
        return out, payload

    def _write_audit(self, rows: list[dict[str, Any]]) -> None:
        self._write_json(self.checkpoints_dir / "step_audit.json", rows)

    def _write_report(self, rows: list[dict[str, Any]]) -> str:
        report_path = self.checkpoints_dir / "step_regression_audit.md"
        lines = ["# Step Regression Audit Report", "", "| step | layer | domain | duration_ms |", "| --- | --- | --- | --- |"]
        for idx, row in enumerate(rows):
            lines.append(f"| {idx} | {row['layer']} | {row['domain']} | {row['duration_ms']:.2f} |")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text("\n".join(lines), encoding="utf-8")
        return str(report_path)

    def run(self, domains: tuple[str, ...] | None = None) -> dict[str, str]:
        selected = domains or self.DEFAULT_DOMAINS
        outputs: dict[str, str] = {}
        audit_rows: list[dict[str, Any]] = []

        for domain in selected:
            l0_path, l0_payload = self._run_l0(domain)
            audit_rows.append({"layer": "layer0", "domain": domain, "duration_ms": l0_payload["metadata"]["metrics"]["duration_ms"]})

            l1_path, l1_payload = self._run_l1(domain, l0_payload["records"])
            audit_rows.append({"layer": "layer1", "domain": domain, "duration_ms": l1_payload["metadata"]["metrics"]["duration_ms"]})
            outputs[domain] = str(l1_path)

        self._write_audit(audit_rows)
        outputs["report"] = self._write_report(audit_rows)
        return outputs
