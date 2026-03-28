import pytest
from scrapers.base.helpers.time import parse_date_parts, parse_date_iso, parse_date_text
from models.value_objects.time_types import DateValue

def test_parse_date_parts():
    assert parse_date_parts("2023-10-27") == (2023, 10, 27)
    assert parse_date_parts("2023-10") == (2023, 10, None)
    assert parse_date_parts("2023") == (2023, None, None)
    assert parse_date_parts("invalid") == (None, None, None)
    assert parse_date_parts("2023-10-27-01") == (None, None, None)

def test_parse_date_iso():
    assert parse_date_iso("27 October 2023") == "2023-10-27"
    assert parse_date_iso("October 2023") == "2023-10"
    assert parse_date_iso("2023") == "2023"
    assert parse_date_iso("invalid") is None

def test_parse_date_text():
    res = parse_date_text("2023-10-27")
    assert res.year == 2023
    assert res.month == 10
    assert res.day == 27
    assert res.iso == ["2023-10-27"]

    res = parse_date_text("October 2023")
    assert res.year == 2023
    assert res.month == 10
    assert res.day is None
    assert res.iso == "2023-10"
