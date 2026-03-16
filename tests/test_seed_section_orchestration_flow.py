import json
from pathlib import Path

from scrapers.wiki.seed_section_orchestration_flow import SeedSectionOrchestrationFlow


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_seed_section_orchestration_l0_l1_for_drivers_and_constructors(
    tmp_path: Path,
) -> None:
    drivers_seed = tmp_path / "data" / "raw" / "drivers" / "drivers.json"
    constructors_seed = tmp_path / "data" / "raw" / "constructors" / "constructors.json"
    drivers_seed.parent.mkdir(parents=True, exist_ok=True)
    constructors_seed.parent.mkdir(parents=True, exist_ok=True)

    drivers_seed.write_text(
        json.dumps(
            [
                {"driver": {"text": "Driver A", "url": "https://example.test/driver-a"}},
                {"driver": {"text": "Driver B", "url": "https://example.test/driver-b"}},
            ],
        ),
        encoding="utf-8",
    )
    constructors_seed.write_text(
        json.dumps(
            [
                {
                    "constructor": {
                        "text": "Constructor A",
                        "url": "https://example.test/constructor-a",
                    },
                },
            ],
        ),
        encoding="utf-8",
    )

    flow = SeedSectionOrchestrationFlow(
        base_dir=tmp_path / "data",
        detail_fetchers={
            "drivers": lambda url: {"url": url, "kind": "driver-section"},
            "constructors": lambda url: {"url": url, "kind": "constructor-section"},
        },
    )

    outputs = flow.run()

    drivers_l0 = _read_json(tmp_path / "data" / "checkpoints" / "step_0_layer0_drivers.json")
    assert len(drivers_l0["records"]) == 2

    drivers_l1 = _read_json(tmp_path / "data" / "checkpoints" / "step_1_layer1_drivers.json")
    assert [record["kind"] for record in drivers_l1["records"]] == [
        "driver-section",
        "driver-section",
    ]

    constructors_l1 = _read_json(
        tmp_path / "data" / "checkpoints" / "step_1_layer1_constructors.json",
    )
    assert constructors_l1["records"][0]["kind"] == "constructor-section"

    report_path = Path(outputs["report"])
    assert report_path.exists()
    report = report_path.read_text(encoding="utf-8")
    assert "# Step Regression Audit Report" in report
    assert "| 1 | layer1 | drivers" in report


def test_section_source_adapter_prefers_checkpoint_before_raw(tmp_path: Path) -> None:
    checkpoints = tmp_path / "data" / "checkpoints"
    raw = tmp_path / "data" / "raw" / "drivers"
    checkpoints.mkdir(parents=True, exist_ok=True)
    raw.mkdir(parents=True, exist_ok=True)

    (checkpoints / "drivers.json").write_text(
        json.dumps({"records": [{"driver": {"url": "https://example.test/checkpoint"}}]}),
        encoding="utf-8",
    )
    (raw / "drivers.json").write_text(
        json.dumps([{"url": "https://example.test/raw"}]),
        encoding="utf-8",
    )

    flow = SeedSectionOrchestrationFlow(
        base_dir=tmp_path / "data",
        detail_fetchers={"drivers": lambda url: {"url": url}},
    )
    flow.run(domains=("drivers",))

    l0_payload = _read_json(tmp_path / "data" / "checkpoints" / "step_0_layer0_drivers.json")
    assert l0_payload["records"] == [{"name": "", "url": "https://example.test/checkpoint"}]


def test_step_metrics_are_logged_for_audit(tmp_path: Path) -> None:
    source = tmp_path / "data" / "checkpoints" / "step_0_layer0_drivers.json"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text(
        json.dumps({"records": [{"driver": {"url": "https://example.test/a"}}]}),
        encoding="utf-8",
    )

    flow = SeedSectionOrchestrationFlow(
        base_dir=tmp_path / "data",
        detail_fetchers={"drivers": lambda url: {"url": url, "ok": True}},
    )
    flow.run(domains=("drivers",))

    layer1_payload = _read_json(tmp_path / "data" / "checkpoints" / "step_1_layer1_drivers.json")
    metrics = layer1_payload["metadata"]["metrics"]
    assert metrics["input_records"] == 1
    assert metrics["output_records"] == 1
    assert metrics["errors"] == 0
    assert isinstance(metrics["duration_ms"], float)

    audit_json = _read_json(tmp_path / "data" / "checkpoints" / "step_audit.json")
    assert isinstance(audit_json[-1]["duration_ms"], float)
