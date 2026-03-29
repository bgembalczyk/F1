from __future__ import annotations

import json
from pathlib import Path

from scrapers.base.orchestration.components.section_soruce_adapter import SectionSourceAdapter
from scrapers.base.orchestration.models import StepDeclaration
from scrapers.base.orchestration.models import StepExecutionResult
from scrapers.wiki.drivers_checkpoint_flow import DriversCheckpointFlow


def test_step_execution_result_lifecycle_across_components(tmp_path: Path) -> None:
    source = tmp_path / "data" / "raw" / "drivers" / "drivers.json"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text(
        json.dumps([{"driver": {"text": "Driver A", "url": "https://example.test/a"}}]),
        encoding="utf-8",
    )

    resolver = SectionSourceAdapter(base_dir=tmp_path / "data")
    declaration = StepDeclaration(
        step_id=0,
        layer="layer0",
        input_source="drivers",
        parser=lambda rows: rows,
        output_target="checkpoints",
    )
    resolved = resolver.resolve(declaration, "drivers")

    assert isinstance(resolved, StepExecutionResult)
    assert resolved.status == "resolved"
    assert resolved.metrics["input_records"] == 1
    assert resolved.source_path == source

    flow = DriversCheckpointFlow(
        source_file=source,
        checkpoint_file=tmp_path / "data" / "checkpoints" / "step_0_layer0_drivers.json",
        layer1_output_file=tmp_path / "data" / "checkpoints" / "step_1_layer1_drivers.json",
        registry_file=tmp_path / "data" / "checkpoints" / "step_registry.json",
        detail_fetcher=lambda url: {"url": url, "kind": "driver"},
    )
    layer0 = flow.run_layer0_checkpoint()
    layer1 = flow.run_layer1_from_checkpoint()

    assert layer0.status == "checkpointed"
    assert layer0.output_paths["checkpoint_path"].endswith("step_0_layer0_drivers.json")

    assert layer1.status == "parsed"
    assert layer1.metrics["input_records"] == 1
    assert layer1.metrics["output_records"] == 1
    assert layer1.output_paths["source_path"].endswith("step_0_layer0_drivers.json")


def test_step_execution_result_with_updates_merges_metrics_and_paths() -> None:
    result = StepExecutionResult.empty().with_updates(
        status="resolved",
        records=[{"url": "https://example.test/a"}],
        metrics={"input_records": 1},
        output_paths={"source_path": "/tmp/source.json"},
    )
    next_result = result.with_updates(
        status="checkpointed",
        metrics={"output_records": 1},
        output_paths={"checkpoint_path": "/tmp/output.json"},
    )

    assert next_result.status == "checkpointed"
    assert next_result.metrics == {"input_records": 1, "output_records": 1}
    assert next_result.output_paths == {
        "source_path": "/tmp/source.json",
        "checkpoint_path": "/tmp/output.json",
    }
