import importlib.util
import json

import pytest

from models.value_objects.normalized_date import NormalizedDate
from scrapers.base.format.csv_formatter import CsvFormatter
from scrapers.base.format.json_formatter import JsonFormatter
from scrapers.base.format.pandas_formatter import PandasDataFrameFormatter
from scrapers.base.helpers.value_objects.normalized_time import NormalizedTime
from scrapers.base.results import ScrapeResult

EXPECTED_TWO_RECORDS = 2


def test_json_formatter_without_metadata() -> None:
    formatter = JsonFormatter()
    data = [{"name": "Ayrton", "wins": 41}]

    payload = formatter.format(data, indent=2, include_metadata=False)

    assert json.loads(payload) == data


def test_json_formatter_handles_empty_data() -> None:
    formatter = JsonFormatter()
    data = []

    payload = formatter.format(data, indent=2, include_metadata=False)

    assert json.loads(payload) == []


def test_json_formatter_with_metadata() -> None:
    formatter = JsonFormatter()
    result = ScrapeResult(
        data=[{"name": "Ayrton", "wins": 41}],
        source_url="https://example.com",
    )

    payload = formatter.format(result, indent=2, include_metadata=True)
    parsed = json.loads(payload)

    assert parsed["meta"]["source_url"] == "https://example.com"
    assert parsed["meta"]["timestamp"]
    assert parsed["meta"]["records_count"] == 1
    assert parsed["data"] == [{"name": "Ayrton", "wins": 41}]


def test_json_formatter_sorts_nested_dict_keys() -> None:
    formatter = JsonFormatter()
    data = [{"z": {"d": 1, "a": 2}, "a": {"y": {"b": 1, "a": 2}}}]

    payload = formatter.format(data, include_metadata=False)

    assert payload.index('"a"') < payload.index('"z"')
    assert payload.index('"a": 2') < payload.index('"d": 1')
    assert payload.index('"a": 2', payload.index('"y"')) < payload.index(
        '"b": 1',
        payload.index('"y"'),
    )


def test_json_formatter_prioritizes_constructor_engine_and_manufacturer_keys() -> None:
    formatter = JsonFormatter()
    data = [
        {
            "points": 1,
            "constructor": {"text": "A"},
            "engine": {"text": "B"},
            "manufacturer": {"text": "C"},
        },
    ]

    payload = formatter.format(data, include_metadata=False)

    assert payload.index('"constructor"') < payload.index('"engine"')
    assert payload.index('"engine"') < payload.index('"manufacturer"')
    assert payload.index('"manufacturer"') < payload.index('"points"')


def test_json_formatter_prioritizes_season_then_grand_prix_or_event_keys() -> None:
    formatter = JsonFormatter()
    grand_prix_data = [
        {
            "winner": {"text": "A"},
            "grand_prix": {"text": "B"},
            "season": 2024,
            "lap": 5,
        },
    ]
    event_data = [
        {
            "winner": {"text": "A"},
            "event": {"text": "B"},
            "season": 1971,
            "lap": 12,
        },
    ]

    grand_prix_payload = formatter.format(grand_prix_data, include_metadata=False)
    event_payload = formatter.format(event_data, include_metadata=False)

    assert grand_prix_payload.index('"season"') < grand_prix_payload.index(
        '"grand_prix"'
    )
    assert grand_prix_payload.index('"grand_prix"') < grand_prix_payload.index('"lap"')
    assert event_payload.index('"season"') < event_payload.index('"event"')
    assert event_payload.index('"event"') < event_payload.index('"lap"')


def test_csv_formatter_builds_union_of_fields() -> None:
    formatter = CsvFormatter()
    result = ScrapeResult(
        data=[
            {"name": "Lewis", "wins": 103},
            {"name": "Michael", "titles": 7},
        ],
        source_url="https://example.com",
    )

    payload = formatter.format(result, include_metadata=True)

    lines = payload.strip().splitlines()
    metadata = json.loads(lines[0].replace("# meta: ", ""))
    assert metadata["source_url"] == "https://example.com"
    assert metadata["records_count"] == EXPECTED_TWO_RECORDS
    assert lines[1].split(",") == ["name", "wins", "titles"]
    assert "Lewis,103," in lines[2]
    assert "Michael,,7" in lines[3]


def test_metadata_is_consistent_between_json_and_csv() -> None:
    formatter_json = JsonFormatter()
    formatter_csv = CsvFormatter()
    result = ScrapeResult(
        data=[{"team": "McLaren"}],
        source_url="https://example.com",
    )

    json_payload = json.loads(formatter_json.format(result, include_metadata=True))
    csv_payload = formatter_csv.format(result, include_metadata=True)
    csv_meta = json.loads(csv_payload.splitlines()[0].replace("# meta: ", ""))

    assert json_payload["meta"] == csv_meta


def test_csv_formatter_handles_empty_data() -> None:
    formatter = CsvFormatter()

    payload = formatter.format([])

    assert payload == ""


def test_dataframe_formatter_handles_optional_dependency() -> None:
    formatter = PandasDataFrameFormatter()
    data = [{"name": "Max", "wins": 54}]

    if importlib.util.find_spec("pandas") is None:  # pragma: no cover - depends on env
        with pytest.warns(RuntimeWarning, match="Pandas nie jest zainstalowane"):
            fallback = formatter.format(data)
        assert fallback == data
    else:
        result_df = formatter.format(data)
        assert list(result_df.columns) == ["name", "wins"]
        assert result_df.iloc[0].to_dict() == data[0]


def test_json_formatter_serializes_normalized_value_objects() -> None:
    formatter = JsonFormatter()
    result = ScrapeResult(
        data=[
            {
                "date": NormalizedDate(text=" 7 June 2019 ", iso=["2019-06-07"]),
                "time": NormalizedTime(text=" 1:23.456 ", seconds="83.456"),
            },
        ],
        source_url="https://example.com",
    )

    payload = formatter.format(result, include_metadata=True)
    parsed = json.loads(payload)

    assert parsed["meta"]["records_count"] == 1
    assert parsed["data"] == [
        {
            "date": {"text": "7 June 2019", "iso": "2019-06-07"},
            "time": {"text": "1:23.456", "seconds": 83.456},
        },
    ]
