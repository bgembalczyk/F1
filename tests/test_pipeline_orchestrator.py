from __future__ import annotations

import json

from pipeline.orchestrator import Layer0Step
from pipeline.orchestrator import PipelineOrchestrator


def test_orchestrator_writes_checkpoint_with_required_fields(tmp_path):
    called = []

    def runner() -> None:
        called.append("ok")

    step = Layer0Step(
        step_id="layer0_test",
        input_source="unit-test",
        parser="FakeParser",
        output_path="data/wiki/test.json",
        runner=runner,
    )

    orchestrator = PipelineOrchestrator(steps=[step], checkpoint_dir=tmp_path)
    orchestrator.run()

    assert called == ["ok"]

    checkpoint_path = tmp_path / "layer0_test.json"
    payload = json.loads(checkpoint_path.read_text(encoding="utf-8"))

    assert payload["step_id"] == "layer0_test"
    assert payload["input_source"] == "unit-test"
    assert payload["parser"] == "FakeParser"
    assert payload["output_path"] == "data/wiki/test.json"
    assert payload["schema_version"] == "1.0"
    assert payload["timestamp"]
