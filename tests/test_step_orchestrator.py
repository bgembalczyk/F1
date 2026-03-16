import json
from pathlib import Path

from scrapers.base.orchestration import SectionSourceAdapter
from scrapers.base.orchestration import StepDeclaration
from scrapers.base.orchestration import StepOrchestrator


def test_section_source_adapter_fallbacks_to_raw(tmp_path: Path) -> None:
    raw_path = tmp_path / "data" / "raw" / "drivers" / "drivers.json"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_text(json.dumps([{"driver": {"url": "x"}}]), encoding="utf-8")

    adapter = SectionSourceAdapter(base_dir=tmp_path / "data")
    step = StepDeclaration(
        step_id=1,
        layer="layer1",
        input_source="drivers",
        parser=lambda rows: rows,
        output_target="checkpoints",
    )

    records, source_path = adapter.resolve(step, "drivers")

    assert source_path == raw_path
    assert records == [{"driver": {"url": "x"}}]


def test_step_orchestrator_writes_standardized_checkpoint(tmp_path: Path) -> None:
    source = tmp_path / "data" / "checkpoints" / "step_0_layer0_drivers.json"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text(
        json.dumps({"records": [{"url": "https://example.test/a"}]}),
        encoding="utf-8",
    )

    orchestrator = StepOrchestrator(base_dir=tmp_path / "data")
    step = StepDeclaration(
        step_id=1,
        layer="layer1",
        input_source="step_0_layer0_drivers",
        parser=lambda rows: [*rows, {"url": "https://example.test/b"}],
        output_target="checkpoints",
    )

    result = orchestrator.run(step, "drivers")
    output_path = Path(result.output_path)

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert output_path.name == "step_1_layer1_drivers.json"
    assert payload["metadata"]["output_target"] == "checkpoints"
    expected_count = 2
    assert len(payload["records"]) == expected_count
