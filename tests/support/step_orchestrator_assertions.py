from __future__ import annotations

import json
from pathlib import Path

from scrapers.base.orchestration.step_orchestrator import SectionSourceAdapter
from scrapers.base.orchestration.step_orchestrator import StepDeclaration


def assert_section_source_adapter_falls_back_to_raw(tmp_path: Path) -> None:
    source = tmp_path / "data" / "raw" / "drivers" / "drivers.json"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text(json.dumps([{"driver": {"url": "x"}}]), encoding="utf-8")

    resolver = SectionSourceAdapter(base_dir=tmp_path / "data")
    step = StepDeclaration(1, "layer1", "drivers", lambda rows: rows, "checkpoints")

    resolved = resolver.resolve(step, "drivers")

    assert resolved.source_path == source
    assert resolved.records == [{"driver": {"url": "x"}}]
