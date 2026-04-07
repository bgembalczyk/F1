# ruff: noqa: E501, PLR2004
import pytest

from models.value_objects.normalized_date import NormalizedDate
from scrapers.circuits.models.services.lap_record_utils import build_lap_record_key
from scrapers.circuits.models.services.lap_record_utils import extract_year
from scrapers.circuits.models.services.lap_record_utils import extract_year_from_event
from scrapers.circuits.models.services.lap_record_utils import has_meaningful_value
from scrapers.circuits.models.services.lap_record_utils import (
    normalize_lap_record_entity,
)
from scrapers.circuits.models.services.lap_record_utils import (
    parse_lap_record_time_from_record,
)
from scrapers.circuits.models.services.lap_record_utils import (
    select_best_field_with_url,
)

# ---------------------------------------------------------------------------
# extract_year_from_event  (lines 19-36)
# ---------------------------------------------------------------------------


def test_extract_year_from_event_dict_text() -> None:
    rec = {"event": {"text": "1963 Aintree 200", "url": None}}
    assert extract_year_from_event(rec) == "1963"


def test_extract_year_from_event_dict_url() -> None:
    # URL must have year at a word boundary (space, not underscore) for \b to match
    rec = {"event": {"url": "https://en.wikipedia.org/wiki/1999 Monaco GP", "text": ""}}
    assert extract_year_from_event(rec) == "1999"


def test_extract_year_from_event_string() -> None:
    rec = {"event": "2001 Austrian Grand Prix"}
    assert extract_year_from_event(rec) == "2001"


def test_extract_year_from_event_no_year() -> None:
    rec = {"event": "Australian Grand Prix"}
    assert extract_year_from_event(rec) is None


def test_extract_year_from_event_no_event() -> None:
    assert extract_year_from_event({}) is None


# ---------------------------------------------------------------------------
# extract_year  (lines 47-57)
# ---------------------------------------------------------------------------


def test_extract_year_from_year_field() -> None:
    rec = {"year": "2019"}
    assert extract_year(rec) == "2019"


def test_extract_year_from_year_field_int() -> None:
    rec = {"year": 2019}
    assert extract_year(rec) == "2019"


def test_extract_year_from_date_dict() -> None:
    rec = {"date": {"iso": "2019-06-23"}}
    assert extract_year(rec) == "2019"


def test_extract_year_from_date_normalized() -> None:
    nd = NormalizedDate(text="29 August 2021", iso="2021-08-29")
    rec = {"date": nd}
    assert extract_year(rec) == "2021"


def test_extract_year_from_event_fallback() -> None:
    rec = {"event": "2003 Austrian GP"}
    assert extract_year(rec) == "2003"


def test_extract_year_none() -> None:
    assert extract_year({}) is None


# ---------------------------------------------------------------------------
# normalize_lap_record_entity  (line 68 – with sanitizer)
# ---------------------------------------------------------------------------


def test_normalize_lap_record_entity_plain() -> None:
    assert normalize_lap_record_entity("Lewis Hamilton") == "lewis hamilton"


def test_normalize_lap_record_entity_dict() -> None:
    assert normalize_lap_record_entity({"text": "Lewis Hamilton"}) == "lewis hamilton"


def test_normalize_lap_record_entity_with_sanitizer() -> None:
    def sanitize(s: str) -> str:
        return s.replace("Hamilton", "Ham")

    result = normalize_lap_record_entity("Lewis Hamilton", sanitizer=sanitize)
    assert "ham" in result


def test_normalize_lap_record_entity_empty() -> None:
    assert normalize_lap_record_entity("") == ""
    assert normalize_lap_record_entity(None) == ""


# ---------------------------------------------------------------------------
# parse_lap_record_time_from_record  (line 88)
# ---------------------------------------------------------------------------


def test_parse_time_from_time_seconds() -> None:
    rec = {"time_seconds": 83.456}
    assert parse_lap_record_time_from_record(rec) == pytest.approx(83.456)


def test_parse_time_from_time_float() -> None:
    rec = {"time": 83.456}
    assert parse_lap_record_time_from_record(rec) == pytest.approx(83.456)


def test_parse_time_from_time_string() -> None:
    rec = {"time": "1:23.456"}
    result = parse_lap_record_time_from_record(rec)
    assert result is not None
    assert result == pytest.approx(83.456, rel=1e-3)


def test_parse_time_none() -> None:
    assert parse_lap_record_time_from_record({}) is None


# ---------------------------------------------------------------------------
# has_meaningful_value  (line 96)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("candidate", "expected"),
    [
        (None, False),
        ("", False),
        ("  ", False),
        ("valid", True),
        ({"text": "value"}, True),
        ({"text": "", "url": None}, False),
        ({"url": "https://example.com"}, True),
        (42, True),
        (0, True),
    ],
)
def test_has_meaningful_value(candidate, expected) -> None:
    assert has_meaningful_value(candidate) == expected


# ---------------------------------------------------------------------------
# select_best_field_with_url  (lines 101-103)
# ---------------------------------------------------------------------------


def test_select_best_field_no_records() -> None:
    assert select_best_field_with_url([], "driver") is None


def test_select_best_field_single() -> None:
    records = [{"driver": {"text": "Hamilton", "url": None}}]
    result = select_best_field_with_url(records, "driver")
    assert result == {"text": "Hamilton", "url": None}


def test_select_best_field_prefers_url() -> None:
    records = [
        {"driver": {"text": "Hamilton", "url": None}},
        {
            "driver": {
                "text": "Hamilton",
                "url": "https://en.wikipedia.org/wiki/Lewis_Hamilton",
            },
        },
    ]
    result = select_best_field_with_url(records, "driver")
    assert result is not None
    assert result.get("url") is not None


def test_select_best_field_multiple_field_names() -> None:
    records = [{"car": {"text": "Ferrari", "url": None}}]
    result = select_best_field_with_url(records, "vehicle", "car")
    assert result == {"text": "Ferrari", "url": None}


def test_select_best_field_skips_none_values() -> None:
    records = [{"driver": None}, {"driver": {"text": "Hamilton", "url": None}}]
    result = select_best_field_with_url(records, "driver")
    assert result is not None


# ---------------------------------------------------------------------------
# build_lap_record_key  (lines 121, 164)
# ---------------------------------------------------------------------------


def test_build_lap_record_key_basic() -> None:
    rec = {
        "driver": {"text": "Lewis Hamilton"},
        "vehicle": {"text": "Mercedes"},
        "year": "2019",
        "time": 83.456,
    }
    key = build_lap_record_key(rec)
    assert key is not None
    assert len(key) == 4


def test_build_lap_record_key_returns_none_when_missing_driver() -> None:
    rec = {"vehicle": {"text": "Mercedes"}, "year": "2019", "time": 83.456}
    assert build_lap_record_key(rec) is None


def test_build_lap_record_key_custom_year_extractor() -> None:
    rec = {
        "driver": {"text": "Hamilton"},
        "vehicle": {"text": "Mercedes"},
        "event": "2020 British Grand Prix",
        "time": 83.456,
    }
    key = build_lap_record_key(rec, year_extractor=extract_year_from_event)
    assert key is not None
    assert "2020" in key


def test_build_lap_record_key_custom_time_key_factory() -> None:
    rec = {
        "driver": {"text": "Hamilton"},
        "vehicle": {"text": "Mercedes"},
        "year": "2019",
        "time": 83.456,
    }
    key = build_lap_record_key(rec, time_key_factory=lambda t: int(t * 1000))
    assert key is not None
    # time should be int(83456)
    assert key[3] == int(83.456 * 1000)


def test_build_lap_record_key_custom_vehicle_getter() -> None:
    rec = {
        "driver": {"text": "Hamilton"},
        "car": {"text": "Mercedes"},
        "year": "2019",
        "time": 83.456,
    }
    key = build_lap_record_key(rec, vehicle_getter=lambda r: r.get("car"))
    assert key is not None


def test_build_lap_record_key_custom_key_order() -> None:
    rec = {
        "driver": {"text": "Hamilton"},
        "vehicle": {"text": "Mercedes"},
        "year": "2019",
        "time": 83.456,
    }
    key = build_lap_record_key(rec, key_order=("year", "driver", "vehicle", "time"))
    assert key is not None
    assert key[0] == "2019"
