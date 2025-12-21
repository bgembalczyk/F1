import csv
import json
from datetime import datetime, timezone

from scrapers.base.results import ScrapeResult


def _read_header(path):
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        return next(reader)


def test_to_csv_union_fieldnames_preserves_order(tmp_path):
    data = [{"b": 1, "a": 2}, {"c": 3, "b": 4}]
    result = ScrapeResult(data=data, source_url=None)
    output = tmp_path / "union.csv"

    result.to_csv(output)

    assert _read_header(output) == ["b", "a", "c"]


def test_to_csv_first_row_fieldnames_preserves_order(tmp_path):
    data = [{"b": 1, "a": 2}, {"a": 3, "b": 4}]
    result = ScrapeResult(data=data, source_url=None)
    output = tmp_path / "first_row.csv"

    result.to_csv(output, fieldnames_strategy="first_row")

    assert _read_header(output) == ["b", "a"]


def test_to_json_includes_metadata_from_result(tmp_path):
    timestamp = datetime(2024, 1, 1, tzinfo=timezone.utc)
    result = ScrapeResult(
        data=[{"driver": "Max"}],
        source_url="https://example.com",
        timestamp=timestamp,
    )
    output = tmp_path / "result.json"

    result.to_json(output, include_metadata=True)

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["meta"]["source_url"] == "https://example.com"
    assert payload["meta"]["timestamp"] == timestamp.isoformat()
    assert payload["data"] == [{"driver": "Max"}]
