from __future__ import annotations

import json

from scrapers.base.exporters import DataExporter


def test_exporter_normalizes_keys_and_drops_empty_fields(tmp_path) -> None:
    exporter = DataExporter(normalize_keys=True)
    data = [
        {"Driver Name": "Max", "Wins": 54, "Notes": ""},
        {"driver name": "Lewis", "wins": 103, "Notes": None},
    ]

    output = tmp_path / "normalized.json"
    exporter.to_json(data, output)

    normalized = json.loads(output.read_text(encoding="utf-8"))

    assert normalized == [
        {"driver_name": "Max", "wins": 54},
        {"driver_name": "Lewis", "wins": 103},
    ]
    assert {frozenset(item.keys()) for item in normalized} == {
        frozenset(["driver_name", "wins"])
    }


def test_exporter_allows_custom_normalization_rules(tmp_path) -> None:
    def rename_wins(record: dict) -> dict:
        if "wins" not in record:
            return record
        value = record.pop("wins")
        record["total_wins"] = value
        return record

    exporter = DataExporter(normalize_keys=True, normalization_rules=[rename_wins])
    data = [{"Wins": 41}]

    output = tmp_path / "custom.json"
    exporter.to_json(data, output)

    normalized = json.loads(output.read_text(encoding="utf-8"))
    assert normalized == [{"total_wins": 41}]
