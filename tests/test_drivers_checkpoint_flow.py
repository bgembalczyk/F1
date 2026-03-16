import json
from pathlib import Path

from scrapers.wiki.drivers_checkpoint_flow import DriversCheckpointFlow


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_layer0_writes_checkpoint_with_metadata(tmp_path: Path) -> None:
    source_file = tmp_path / "data" / "wiki" / "drivers" / "f1_drivers.json"
    source_file.parent.mkdir(parents=True, exist_ok=True)
    source_file.write_text(
        json.dumps(
            [
                {
                    "driver": {
                        "text": "Max Verstappen",
                        "url": "https://example.test/max",
                    },
                },
            ],
        ),
        encoding="utf-8",
    )

    checkpoint_file = tmp_path / "data" / "checkpoints" / "step_0_layer0_drivers.json"
    output_file = tmp_path / "data" / "raw" / "drivers" / "step_1_layer1_drivers.json"
    registry_file = tmp_path / "data" / "checkpoints" / "step_registry.json"

    flow = DriversCheckpointFlow(
        source_file=source_file,
        checkpoint_file=checkpoint_file,
        layer1_output_file=output_file,
        registry_file=registry_file,
    )

    flow.run_layer0_checkpoint()

    payload = _read_json(checkpoint_file)
    assert payload["metadata"]["source_file"] == str(source_file)
    assert payload["metadata"]["source_category"] == "drivers"
    assert payload["metadata"]["parser_version"] == "drivers-checkpoint-flow-v1"
    assert payload["metadata"]["scraped_at"]
    assert payload["records"] == [
        {"name": "Max Verstappen", "url": "https://example.test/max"},
    ]


def test_layer1_reads_only_checkpoint_urls_and_is_idempotent(tmp_path: Path) -> None:
    source_file = tmp_path / "data" / "wiki" / "drivers" / "f1_drivers.json"
    source_file.parent.mkdir(parents=True, exist_ok=True)
    source_file.write_text(
        json.dumps(
            [
                {
                    "driver": {
                        "text": "Driver A",
                        "url": "https://example.test/a",
                    },
                },
                {
                    "driver": {
                        "text": "Driver B",
                        "url": "https://example.test/b",
                    },
                },
            ],
        ),
        encoding="utf-8",
    )

    checkpoint_file = tmp_path / "data" / "checkpoints" / "step_0_layer0_drivers.json"
    output_file = tmp_path / "data" / "raw" / "drivers" / "step_1_layer1_drivers.json"
    registry_file = tmp_path / "data" / "checkpoints" / "step_registry.json"

    calls: list[str] = []

    def fake_fetcher(url: str):
        calls.append(url)
        return {"url": url, "driver": {"name": url.rsplit("/", maxsplit=1)[-1]}}

    flow = DriversCheckpointFlow(
        source_file=source_file,
        checkpoint_file=checkpoint_file,
        layer1_output_file=output_file,
        registry_file=registry_file,
        detail_fetcher=fake_fetcher,
    )

    flow.run_layer0_checkpoint()

    checkpoint_payload = _read_json(checkpoint_file)
    checkpoint_payload["records"].append(
        {"name": "Only checkpoint", "url": "https://example.test/c"},
    )
    checkpoint_file.write_text(json.dumps(checkpoint_payload), encoding="utf-8")

    flow.run_layer1_from_checkpoint()
    flow.run_layer1_from_checkpoint()

    assert calls == [
        "https://example.test/a",
        "https://example.test/b",
        "https://example.test/c",
    ]

    output_payload = _read_json(output_file)
    assert [item["url"] for item in output_payload] == calls

    registry_payload = _read_json(registry_file)
    recorded_steps = {entry["step"]: entry for entry in registry_payload["steps"]}
    assert recorded_steps["step_0_layer0_drivers"]["input"] == str(source_file)
    assert recorded_steps["step_1_layer1_drivers"]["input"] == str(checkpoint_file)
    assert recorded_steps["step_1_layer1_drivers"]["output"] == str(output_file)
