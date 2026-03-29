from __future__ import annotations

from pathlib import Path
from typing import Any

from scrapers.base.orchestration.components.section_soruce_adapter import SectionSourceAdapter
from scrapers.base.orchestration.models import StepDeclaration
from scrapers.wiki.drivers_checkpoint_flow import DriversCheckpointFlow


def _extract_name(record: dict[str, Any]) -> str:
    for key in ("name", "driver", "constructor", "circuit", "season", "grand_prix"):
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
        if isinstance(value, dict):
            text = value.get("text") or value.get("name")
            if text:
                return str(text).strip()
    return ""


def _extract_url(record: dict[str, Any]) -> str | None:
    for key in ("url", "driver", "constructor", "circuit", "season", "grand_prix"):
        value = record.get(key)
        if isinstance(value, str) and value.strip().startswith("http"):
            return value.strip()
        if isinstance(value, dict):
            url = value.get("url") or value.get("link")
            if url:
                return str(url).strip()
    return None


class SeedSectionOrchestrationFlow:
    def __init__(
        self,
        *,
        base_dir: Path = Path("data"),
        detail_fetchers: dict[str, Any] | None = None,
    ) -> None:
        self._base_dir = base_dir
        self._resolver = SectionSourceAdapter(base_dir=base_dir)
        self._detail_fetchers = detail_fetchers or {}

    def run(
        self,
        *,
        domains: tuple[str, ...] = (
            "drivers",
            "constructors",
            "circuits",
            "seasons",
            "grands_prix",
        ),
    ) -> dict[str, str]:
        outputs: dict[str, str] = {}

        for domain in domains:
            l0_step = StepDeclaration(
                step_id=0,
                layer="layer0",
                input_source=domain,
                parser=lambda rows: rows,
                output_target="checkpoints",
            )
            resolved = self._resolver.resolve(l0_step, domain)
            source_path = resolved.source_path
            if source_path is None:
                continue

            checkpoint_dir = self._base_dir / "checkpoints"
            l0_checkpoint = checkpoint_dir / f"step_0_layer0_{domain}.json"
            l1_checkpoint = checkpoint_dir / f"step_1_layer1_{domain}.json"
            registry_file = checkpoint_dir / "step_registry.json"

            flow = DriversCheckpointFlow(
                source_file=source_path,
                checkpoint_file=l0_checkpoint,
                layer1_output_file=l1_checkpoint,
                registry_file=registry_file,
                detail_fetcher=self._build_detail_fetcher(domain),
            )
            flow.run_layer0_checkpoint()
            flow.run_layer1_from_checkpoint()
            outputs[domain] = str(l1_checkpoint)

        report_path = self._base_dir / "checkpoints" / "step_audit_report.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(self._render_report(), encoding="utf-8")
        outputs["report"] = str(report_path)
        return outputs

    def _build_detail_fetcher(self, domain: str):
        return self._detail_fetchers.get(domain, lambda url: {"url": url})

    def _render_report(self) -> str:
        audit_json = self._base_dir / "checkpoints" / "step_audit.json"
        if not audit_json.exists():
            return "# Step Regression Audit Report\n\nBrak danych audit.\n"

        import json

        rows = json.loads(audit_json.read_text(encoding="utf-8"))
        lines = [
            "# Step Regression Audit Report",
            "",
            "| step_id | layer | domain | input_records | output_records | duration_ms |",
            "|---:|---|---|---:|---:|---:|",
        ]
        for row in rows:
            lines.append(
                "| {step_id} | {layer} | {domain} | {input_records} | {output_records} | {duration_ms:.3f} |".format(
                    step_id=row.get("step_id", ""),
                    layer=row.get("layer", ""),
                    domain=row.get("domain", ""),
                    input_records=row.get("input_records", 0),
                    output_records=row.get("output_records", 0),
                    duration_ms=float(row.get("duration_ms", 0.0)),
                ),
            )
        lines.append("")
        return "\n".join(lines)
