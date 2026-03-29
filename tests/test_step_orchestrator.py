import json
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


def test_section_source_adapter_normalizes_dict_payload_before_parser_contract(
    tmp_path: Path,
) -> None:
    source = tmp_path / "data" / "raw" / "drivers" / "drivers.json"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text(
        json.dumps(
            {
                "records": [
                    {"driver": {"url": "x"}},
                    "invalid-record",
                    123,
                ],
            },
        ),
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

    assert resolved.records == [{"driver": {"url": "x"}}]
