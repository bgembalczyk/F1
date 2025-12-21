from __future__ import annotations

import json

import importlib.util

import pytest

from scrapers.base.formatters import CsvFormatter, JsonFormatter, PandasDataFrameFormatter
from scrapers.base.results import ScrapeResult


def test_json_formatter_without_metadata() -> None:
    formatter = JsonFormatter()
    data = [{"name": "Ayrton", "wins": 41}]

    payload = formatter.format(data, indent=2, include_metadata=False)

    assert json.loads(payload) == data


def test_json_formatter_with_metadata() -> None:
    formatter = JsonFormatter()
    result = ScrapeResult(data=[{"team": "McLaren"}], source_url="https://example.com")

    payload = formatter.format(result, include_metadata=True)
    parsed = json.loads(payload)

    assert parsed["meta"]["source_url"] == "https://example.com"
    assert parsed["meta"]["timestamp"]
    assert parsed["data"] == [{"team": "McLaren"}]


def test_csv_formatter_builds_union_of_fields() -> None:
    formatter = CsvFormatter()
    data = [
        {"name": "Lewis", "wins": 103},
        {"name": "Michael", "titles": 7},
    ]

    payload = formatter.format(data)

    lines = payload.strip().splitlines()
    assert lines[0].split(",") == ["name", "wins", "titles"]
    assert "Lewis,103," in lines[1]
    assert "Michael,,7" in lines[2]


def test_dataframe_formatter_handles_optional_dependency() -> None:
    formatter = PandasDataFrameFormatter()
    data = [{"name": "Max", "wins": 54}]

    if importlib.util.find_spec("pandas") is None:  # pragma: no cover - depends on env
        with pytest.warns(RuntimeWarning, match="Pandas nie jest zainstalowane"):
            fallback = formatter.format(data)
        assert fallback == data
    else:
        import pandas as pd  # noqa: F401

        df = formatter.format(data)
        assert list(df.columns) == ["name", "wins"]
        assert df.iloc[0].to_dict() == data[0]
