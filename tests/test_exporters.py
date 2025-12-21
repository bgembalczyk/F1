import csv

from scrapers.base.exporters import DataExporter


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
