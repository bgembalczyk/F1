from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Callable

KEY_BY_DOMAIN = {
    "drivers": "driver",
    "constructors": "constructor",
    "circuits": "circuit",
    "seasons": "season",
    "grands_prix": "grand_prix",
}


class SeedSectionOrchestrationFlow:
    def __init__(
        self,
        *,
        base_dir: Path,
        detail_fetchers: dict[str, Callable[[str], dict[str, Any]]],
    ) -> None:
        self.base_dir = base_dir
        self.detail_fetchers = detail_fetchers
        self.checkpoints_dir = base_dir / "checkpoints"

    def _read_json(self, path: Path, default: Any) -> Any:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))

    def _write_json(self, path: Path, payload: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    def _load_seed_records(self, domain: str) -> list[dict[str, Any]]:
        checkpoint_seed = self.checkpoints_dir / f"{domain}.json"
        if checkpoint_seed.exists():
            payload = self._read_json(checkpoint_seed, {})
            return payload.get("records", []) if isinstance(payload, dict) else []
        return self._read_json(self.base_dir / "raw" / domain / f"{domain}.json", [])

    def _extract_urls(self, domain: str, records: list[dict[str, Any]]) -> list[dict[str, str]]:
        key = KEY_BY_DOMAIN.get(domain, domain.rstrip("s"))
        extracted: list[dict[str, str]] = []
        for item in records:
            candidate = item.get(key) if isinstance(item, dict) else None
            if isinstance(candidate, dict):
                url = str(candidate.get("url") or "")
                if url:
                    extracted.append({"name": str(candidate.get("text") or ""), "url": url})
                    continue
            if isinstance(item, dict):
                url = str(item.get("url") or "")
                if url:
                    extracted.append({"name": str(item.get("name") or ""), "url": url})
        return extracted

    def _append_audit(self, entry: dict[str, Any]) -> None:
        path = self.checkpoints_dir / "step_audit.json"
        audit = self._read_json(path, [])
        audit.append(entry)
        self._write_json(path, audit)

    def _write_report(self) -> Path:
        audit = self._read_json(self.checkpoints_dir / "step_audit.json", [])
        lines = ["# Step Regression Audit Report", "", "| step | layer | domain |", "|---:|---|---|"]
        for item in audit:
            lines.append(f"| {item.get('step_id')} | {item.get('layer')} | {item.get('domain')} |")
        report_path = self.checkpoints_dir / "step_report.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text("\n".join(lines), encoding="utf-8")
        return report_path

    def run(self, domains: tuple[str, ...] | None = None) -> dict[str, str]:
        target_domains = domains or tuple(self.detail_fetchers.keys())
        outputs: dict[str, str] = {}

        for domain in target_domains:
            seed_records = self._load_seed_records(domain)
            l0_records = self._extract_urls(domain, seed_records)
            l0_path = self.checkpoints_dir / f"step_0_layer0_{domain}.json"
            self._write_json(l0_path, {"metadata": {"domain": domain}, "records": l0_records})

            started = time.perf_counter()
            l1_records: list[dict[str, Any]] = []
            errors = 0
            fetcher = self.detail_fetchers.get(domain, lambda url: {"url": url})
            for record in l0_records:
                url = record.get("url", "")
                if not url:
                    continue
                try:
                    details = fetcher(url)
                except Exception:
                    errors += 1
                    continue
                l1_records.append({"name": record.get("name", ""), "url": url, "details": details})

            duration_ms = (time.perf_counter() - started) * 1000
            l1_path = self.checkpoints_dir / f"step_1_layer1_{domain}.json"
            self._write_json(
                l1_path,
                {
                    "metadata": {
                        "metrics": {
                            "input_records": len(l0_records),
                            "output_records": len(l1_records),
                            "errors": errors,
                            "duration_ms": duration_ms,
                        },
                    },
                    "records": l1_records,
                },
            )
            self._append_audit(
                {
                    "step_id": 1,
                    "layer": "layer1",
                    "domain": domain,
                    "duration_ms": duration_ms,
                },
            )
            outputs[domain] = str(l1_path)

        outputs["report"] = str(self._write_report())
        return outputs
