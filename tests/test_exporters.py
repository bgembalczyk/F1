import csv

from scrapers.base.export.exporters import DataExporter
from scrapers.base.results import ScrapeResult


def _read_header(path):
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        return next(reader)


def test_to_csv_union_fieldnames_preserves_order(tmp_path):
    exporter = DataExporter()
    data = [{"b": 1, "a": 2}, {"c": 3, "b": 4}]
    output = tmp_path / "union.csv"

    exporter.to_csv(data, output)

    assert _read_header(output) == ["b", "a", "c"]


def test_to_csv_first_row_fieldnames_preserves_order(tmp_path):
    exporter = DataExporter()
    data = [{"b": 1, "a": 2}, {"a": 3, "b": 4}]
    output = tmp_path / "first_row.csv"

    exporter.to_csv(data, output, fieldnames_strategy="first_row")

    assert _read_header(output) == ["b", "a"]


def test_to_csv_matches_for_list_and_result(tmp_path):
    exporter = DataExporter()
    data = [{"name": "Max", "wins": 54}, {"name": "Lewis", "wins": 103}]
    result = ScrapeResult(data=data, source_url=None)

    output_list = tmp_path / "list.csv"
    output_result = tmp_path / "result.csv"

    exporter.to_csv(data, output_list)
    exporter.to_csv(result, output_result)

    assert output_list.read_text(encoding="utf-8") == output_result.read_text(
        encoding="utf-8"
    )
