import csv
import json
from datetime import datetime
from datetime import timezone

from scrapers.base.export.service import ExportService
from scrapers.base.results import ScrapeResult
from scrapers.base.services.result_export_service import ResultExportService

EXPECTED_TWO_RECORDS = 2


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

    ResultExportService().to_csv(result, output, include_metadata=True)

    metadata = _read_metadata(output)
    assert metadata["records_count"] == EXPECTED_TWO_RECORDS
    assert _read_header(output) == ["b", "a", "c"]


def test_to_csv_first_row_fieldnames_preserves_order(tmp_path):
    data = [{"b": 1, "a": 2}, {"a": 3, "b": 4}]
    result = ScrapeResult(data=data, source_url=None)
    output = tmp_path / "first_row.csv"

    ResultExportService().to_csv(
        result,
        output,
        fieldnames_strategy="first_row",
        include_metadata=True,
    )

    metadata = _read_metadata(output)
    assert metadata["records_count"] == EXPECTED_TWO_RECORDS
    assert _read_header(output) == ["b", "a"]


def test_to_json_includes_metadata_from_result(tmp_path):
    timestamp = datetime(2024, 1, 1, tzinfo=timezone.utc)
    result = ScrapeResult(
        data=[{"driver": "Max"}],
        source_url="https://example.com",
        timestamp=timestamp,
    )
    output = tmp_path / "result.json"

    ResultExportService().to_json(result, output, include_metadata=True)

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

    ResultExportService().to_json(result, output)

    payload = json.loads(output.read_text(encoding="utf-8"))
    # By default, should return just the data array without meta wrapper
    assert isinstance(payload, list)
    assert len(payload) == EXPECTED_TWO_RECORDS
    assert payload[0]["driver"] == "Lewis"
    assert payload[1]["driver"] == "Max"


def test_to_json_sorts_keys_alphabetically(tmp_path):
    result = ScrapeResult(
        data=[{"zeta": 1, "alpha": 2}],
        source_url="https://example.com",
    )
    output = tmp_path / "result.json"

    ResultExportService().to_json(result, output, include_metadata=True)

    content = output.read_text(encoding="utf-8")
    assert content.index('"alpha"') < content.index('"zeta"')
    assert content.index('"data"') < content.index('"meta"')


def test_to_json_pins_driver_and_team_keys_before_alphabetical(tmp_path):
    result = ScrapeResult(
        data=[
            {"zeta": 1, "driver": "A", "alpha": 2},
            {"zeta": 1, "team": "B", "alpha": 2},
        ],
        source_url="https://example.com",
    )
    output = tmp_path / "result.json"

    ResultExportService().to_json(result, output)

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert list(payload[0])[:2] == ["driver", "alpha"]
    assert list(payload[1])[:2] == ["team", "alpha"]


def test_to_csv_excludes_metadata_by_default(tmp_path):
    result = ScrapeResult(
        data=[{"driver": "Lewis"}, {"driver": "Max"}],
        source_url="https://example.com",
    )
    output = tmp_path / "result.csv"

    ResultExportService().to_csv(result, output)

    content = output.read_text(encoding="utf-8")
    # By default, should not include metadata comment
    assert not content.startswith("# meta:")
    lines = content.strip().split("\n")
    assert lines[0] == "driver"
    assert "Lewis" in lines[1]
    assert "Max" in lines[2]


class _SpyExporter:
    def __init__(self) -> None:
        self.csv_calls = []
        self.json_calls = []

    def to_json(self, result, path, *, indent=2, include_metadata=False) -> None:
        self.json_calls.append((result, path, indent, include_metadata))

    def to_csv(self, result, path, *, fieldnames=None, include_metadata=False) -> None:
        self.csv_calls.append((result, path, fieldnames, include_metadata))


class _SpyFieldnamesStrategy:
    def __init__(self) -> None:
        self.calls = []

    def resolve(self, data, *, strategy):
        self.calls.append((data, strategy))
        return ["driver", "wins"]


class _SpyDataFrameFormatter:
    def __init__(self) -> None:
        self.calls = []

    def format(self, result):
        self.calls.append(result)
        return {"rows": len(result.data)}


def test_to_csv_uses_injected_fieldnames_strategy_without_monkeypatching(tmp_path):
    spy_exporter = _SpyExporter()
    spy_strategy = _SpyFieldnamesStrategy()
    service = ExportService(
        exporter=spy_exporter,
        fieldnames_strategy=spy_strategy,
        dataframe_formatter=_SpyDataFrameFormatter(),
    )
    result = ScrapeResult(
        data=[{"driver": "Max", "wins": 54}],
        source_url=None,
        export_service=service,
    )

    output = tmp_path / "spy.csv"
    result.to_csv(output, fieldnames_strategy="first_row")

    assert spy_strategy.calls
    assert spy_strategy.calls[0][1] == "first_row"
    assert spy_exporter.csv_calls[0][2] == ["driver", "wins"]


def test_to_dataframe_uses_injected_formatter_without_monkeypatching():
    spy_formatter = _SpyDataFrameFormatter()
    service = ExportService(
        exporter=_SpyExporter(),
        fieldnames_strategy=_SpyFieldnamesStrategy(),
        dataframe_formatter=spy_formatter,
    )
    result = ScrapeResult(
        data=[{"driver": "Max"}, {"driver": "Lewis"}],
        source_url=None,
        export_service=service,
    )

    payload = result.to_dataframe()

    assert payload == {"rows": EXPECTED_TWO_RECORDS}
    assert spy_formatter.calls
    assert spy_formatter.calls[0] is result
