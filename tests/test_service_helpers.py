# ruff: noqa: E501, PLR2004

from models.services.helpers import expand_all
from models.services.helpers import normalize_date_value
from models.services.helpers import prune_empty
from models.value_objects.normalized_date import NormalizedDate
from models.value_objects.time_types import DateValue


# expand_all - lines 22-24
def test_expand_all_returns_empty_for_none() -> None:
    assert expand_all(None) == []


def test_expand_all_returns_empty_for_zero() -> None:
    assert expand_all(0) == []


def test_expand_all_returns_empty_for_negative() -> None:
    assert expand_all(-5) == []


def test_expand_all_returns_range_for_positive() -> None:
    assert expand_all(5) == [1, 2, 3, 4, 5]


def test_expand_all_returns_single_for_one() -> None:
    assert expand_all(1) == [1]


# normalize_date_value with DateValue - lines 37-53
def test_normalize_date_value_with_date_value_iso_string() -> None:
    rec: dict = {"date": DateValue(iso="2024-03-15", raw="15 March 2024")}
    normalize_date_value(rec)
    assert rec["date"] == "2024-03-15"


def test_normalize_date_value_with_date_value_iso_list() -> None:
    rec: dict = {"date": DateValue(iso=["2024-03-15", "2024-03-16"], raw="March 2024")}
    normalize_date_value(rec)
    assert rec["date"] == "2024-03-15"


def test_normalize_date_value_with_date_value_empty_iso_list() -> None:
    rec: dict = {"date": DateValue(iso=[], raw="March 2024")}
    normalize_date_value(rec)
    assert rec["date"] is None


def test_normalize_date_value_with_date_value_no_iso_uses_raw() -> None:
    rec: dict = {"date": DateValue(iso=None, raw="March 2024")}
    normalize_date_value(rec)
    assert rec["date"] == "March 2024"


def test_normalize_date_value_with_normalized_date_iso() -> None:
    rec: dict = {"date": NormalizedDate(iso="2024-05-01", text="1 May 2024")}
    normalize_date_value(rec)
    assert rec["date"] == "2024-05-01"


def test_normalize_date_value_with_normalized_date_no_iso_uses_text() -> None:
    rec: dict = {"date": NormalizedDate(iso=None, text="1 May 2024")}
    normalize_date_value(rec)
    assert rec["date"] == "1 May 2024"


def test_normalize_date_value_skips_non_date_field() -> None:
    rec: dict = {"date": "2024-03-15"}
    normalize_date_value(rec)
    # plain string is not a dict or DateValue/NormalizedDate, so untouched
    assert rec["date"] == "2024-03-15"


def test_normalize_date_value_with_dict_iso() -> None:
    rec: dict = {"date": {"iso": "2024-06-01", "text": "1 June 2024"}}
    normalize_date_value(rec)
    assert rec["date"] == "2024-06-01"


# prune_empty with drop_url_none - line 102
def test_prune_empty_drops_url_none_when_flag_set() -> None:
    obj = {"name": "Max", "url": None, "wins": 5}
    result = prune_empty(obj, drop_url_none=True)
    assert "url" not in result
    assert result["name"] == "Max"


def test_prune_empty_keeps_url_none_when_flag_not_set() -> None:
    obj = {"name": "Max", "url": None}
    result = prune_empty(obj, drop_url_none=False, drop_none=False)
    assert "url" in result
    assert result["url"] is None


def test_prune_empty_drop_url_none_in_nested_dict() -> None:
    obj = {"driver": {"name": "Max", "url": None}}
    result = prune_empty(obj, drop_url_none=True)
    assert result == {"driver": {"name": "Max"}}
