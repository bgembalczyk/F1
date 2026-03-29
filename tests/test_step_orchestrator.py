import json
import time
from pathlib import Path

from scrapers.base.orchestration.components.section_soruce_adapter import (
    SectionSourceAdapter,
)
from scrapers.base.orchestration.models import StepDeclaration
from tests.support.step_orchestrator_assertions import (
    assert_section_source_adapter_falls_back_to_raw,
)


def test_section_source_adapter_fallbacks_to_raw(tmp_path: Path) -> None:
    assert_section_source_adapter_falls_back_to_raw(tmp_path)


def test_section_source_adapter_fallbacks_to_legacy_wiki(tmp_path: Path) -> None:
    legacy_path = tmp_path / "data" / "wiki" / "drivers" / "drivers.json"
    legacy_path.parent.mkdir(parents=True, exist_ok=True)
    legacy_path.write_text(
        json.dumps([{"driver": {"url": "legacy"}}]),
        encoding="utf-8",
    )

    adapter = SectionSourceAdapter(base_dir=tmp_path / "data")
    step = StepDeclaration(
        step_id=1,
        layer="layer1",
        input_source="drivers",
        parser=lambda rows: rows,
        output_target="checkpoints",
    )

    resolved = adapter.resolve(step, "drivers")

    assert resolved.source_path == legacy_path
    assert resolved.records == [{"driver": {"url": "legacy"}}]


def test_section_source_adapter_prefers_highest_step_checkpoint_match(
    tmp_path: Path,
) -> None:
    checkpoints_dir = tmp_path / "data" / "checkpoints"
    checkpoints_dir.mkdir(parents=True, exist_ok=True)

    low_step = checkpoints_dir / "step_2_layer1_drivers.json"
    high_step = checkpoints_dir / "step_10_layer1_drivers.json"
    low_step.write_text(json.dumps([{"driver": {"url": "step-2"}}]), encoding="utf-8")
    high_step.write_text(json.dumps([{"driver": {"url": "step-10"}}]), encoding="utf-8")

    adapter = SectionSourceAdapter(base_dir=tmp_path / "data")
    step = StepDeclaration(
        step_id=1,
        layer="layer1",
        input_source="non_existing_source",
        parser=lambda rows: rows,
        output_target="checkpoints",
    )

    resolved = adapter.resolve(step, "drivers")

    assert resolved.source_path == high_step
    assert resolved.records == [{"driver": {"url": "step-10"}}]


def test_section_source_adapter_prefers_newest_raw_match_when_no_step_number(
    tmp_path: Path,
) -> None:
    raw_dir = tmp_path / "data" / "raw" / "drivers"
    raw_dir.mkdir(parents=True, exist_ok=True)

    older = raw_dir / "drivers_source_a.json"
    newer = raw_dir / "drivers_source_b.json"
    older.write_text(json.dumps([{"driver": {"url": "old"}}]), encoding="utf-8")
    time.sleep(0.01)
    newer.write_text(json.dumps([{"driver": {"url": "new"}}]), encoding="utf-8")

    adapter = SectionSourceAdapter(base_dir=tmp_path / "data")
    step = StepDeclaration(
        step_id=1,
        layer="layer1",
        input_source="non_existing_source",
        parser=lambda rows: rows,
        output_target="checkpoints",
    )

    resolved = adapter.resolve(step, "drivers")

    assert resolved.source_path == newer
    assert resolved.records == [{"driver": {"url": "new"}}]
