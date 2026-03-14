import csv
import json
from datetime import datetime
from datetime import timezone

from scrapers.base.results import ScrapeResult


def _read_header(path):
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        for row in reader:
            if row and row[0].startswith("# meta: "):
                continue
            return row
    return []


def _read_metadata(path):
    with path.open(encoding="utf-8") as handle:
        line = handle.readline().strip()
    if not line.startswith("# meta: "):
        msg = "Missing metadata line in CSV export."
        raise AssertionError(msg)
    return json.loads(line.replace("# meta: ", ""))


def test_to_csv_union_fieldnames_preserves_order(tmp_path):
    data = [{"b": 1, "a": 2}, {"c": 3, "b": 4}]
    result = ScrapeResult(data=data, source_url=None)
    output = tmp_path / "union.csv"

    result.to_csv(output, include_metadata=True)

    metadata = _read_metadata(output)
    assert metadata["records_count"] == 2
    assert _read_header(output) == ["b", "a", "c"]


def test_to_csv_first_row_fieldnames_preserves_order(tmp_path):
    data = [{"b": 1, "a": 2}, {"a": 3, "b": 4}]
    result = ScrapeResult(data=data, source_url=None)
    output = tmp_path / "first_row.csv"

    result.to_csv(output, fieldnames_strategy="first_row", include_metadata=True)

    metadata = _read_metadata(output)
    assert metadata["records_count"] == 2
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
    assert payload["meta"]["records_count"] == 1
    assert payload["data"] == [{"driver": "Max"}]


def test_to_json_excludes_metadata_by_default(tmp_path):
    result = ScrapeResult(
        data=[{"driver": "Lewis"}, {"driver": "Max"}],
        source_url="https://example.com",
    )
    output = tmp_path / "result.json"

    result.to_json(output)

    payload = json.loads(output.read_text(encoding="utf-8"))
    # By default, should return just the data array without meta wrapper
    assert isinstance(payload, list)
    assert len(payload) == 2
    assert payload[0]["driver"] == "Lewis"
    assert payload[1]["driver"] == "Max"


def test_to_csv_excludes_metadata_by_default(tmp_path):
    result = ScrapeResult(
        data=[{"driver": "Lewis"}, {"driver": "Max"}],
        source_url="https://example.com",
    )
    output = tmp_path / "result.csv"

    result.to_csv(output)

    content = output.read_text(encoding="utf-8")
    # By default, should not include metadata comment
    assert not content.startswith("# meta:")
    lines = content.strip().split("\n")
    assert lines[0] == "driver"
    assert "Lewis" in lines[1]
    assert "Max" in lines[2]
