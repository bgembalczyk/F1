import csv
import io
import json

import pytest

from scrapers.base.results import ScrapeResult


def _parse_csv_rows(path):
    content = path.read_text(encoding="utf-8")
    reader = csv.DictReader(io.StringIO(content))
    return list(reader)


def _normalize_csv_values(rows):
    normalized = []
    for row in rows:
        normalized.append({key: (value if value != "" else None) for key, value in row.items()})
    return normalized


def test_export_strategies_produce_consistent_normalized_records(tmp_path):
    sample = [
        {"Driver Name": "Max", "Wins": 54, "Notes": ""},
        {"driver name": "Lewis", "wins": 103, "Notes": None},
    ]
    result = ScrapeResult(data=sample, source_url="https://example.com")

    json_path = tmp_path / "sample.json"
    csv_path = tmp_path / "sample.csv"

    result.to_json(json_path, normalize_keys=True)
    result.to_csv(csv_path, normalize_keys=True)

    json_payload = json.loads(json_path.read_text(encoding="utf-8"))
    csv_payload = _normalize_csv_values(_parse_csv_rows(csv_path))

    assert json_payload == [
        {"driver_name": "Max", "wins": 54},
        {"driver_name": "Lewis", "wins": 103},
    ]
    assert csv_payload == [
        {"driver_name": "Max", "wins": "54"},
        {"driver_name": "Lewis", "wins": "103"},
    ]

    try:
        df_payload = result.to_dataframe(normalize_keys=True)
    except ImportError:  # pragma: no cover - depends on env
        pytest.skip("pandas is not installed in this environment")

    assert df_payload.to_dict(orient="records") == json_payload


def test_prepare_for_export_validates_fieldnames_strategy():
    result = ScrapeResult(data=[{"driver": "Max"}], source_url=None)

    with pytest.raises(ValueError, match="Nieznana strategia fieldnames"):
        result.prepare_for_export(fieldnames_strategy="invalid")
