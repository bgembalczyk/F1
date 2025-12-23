import json

from scrapers.base.results import ScrapeResult


def test_exporter_normalizes_keys_and_drops_empty_fields(tmp_path) -> None:
    data = [
        {"Driver Name": "Max", "Wins": 54, "Notes": ""},
        {"driver name": "Lewis", "wins": 103, "Notes": None},
    ]
    result = ScrapeResult(data=data, source_url=None)

    output = tmp_path / "normalized.json"
    result.to_json(output, normalize_keys=True)

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

    data = [{"Wins": 41}]
    result = ScrapeResult(data=data, source_url=None)

    output = tmp_path / "custom.json"
    result.to_json(
        output,
        normalize_keys=True,
        normalization_rules=[rename_wins],
    )

    normalized = json.loads(output.read_text(encoding="utf-8"))
    assert normalized == [{"total_wins": 41}]


def test_exporter_json_matches_for_list_and_result(tmp_path) -> None:
    data = [{"driver": "Max"}, {"driver": "Lewis"}]
    result = ScrapeResult(data=data, source_url=None)

    output_list = tmp_path / "list.json"
    output_result = tmp_path / "result.json"

    ScrapeResult(data=data, source_url=None).to_json(output_list)
    result.to_json(output_result)

    assert output_list.read_text(encoding="utf-8") == output_result.read_text(
        encoding="utf-8"
    )
