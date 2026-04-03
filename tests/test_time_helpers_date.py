from scrapers.base.helpers.time import parse_date_iso
from scrapers.base.helpers.time import parse_date_parts
from scrapers.base.helpers.time import parse_date_text

EXPECTED_YEAR = 2023
EXPECTED_MONTH = 10
EXPECTED_DAY = 27


def test_parse_date_parts():
    assert parse_date_parts("2023-10-27") == (
        EXPECTED_YEAR,
        EXPECTED_MONTH,
        EXPECTED_DAY,
    )
    assert parse_date_parts("2023-10") == (EXPECTED_YEAR, EXPECTED_MONTH, None)
    assert parse_date_parts("2023") == (EXPECTED_YEAR, None, None)
    assert parse_date_parts("invalid") == (None, None, None)
    assert parse_date_parts("2023-10-27-01") == (None, None, None)


def test_parse_date_iso():
    assert parse_date_iso("27 October 2023") == "2023-10-27"
    assert parse_date_iso("October 2023") == "2023-10"
    assert parse_date_iso("2023") == "2023"
    assert parse_date_iso("invalid") is None


def test_parse_date_text():
    res = parse_date_text("2023-10-27")
    assert res.year == EXPECTED_YEAR
    assert res.month == EXPECTED_MONTH
    assert res.day == EXPECTED_DAY
    assert res.iso == ["2023-10-27"]

    res = parse_date_text("October 2023")
    assert res.year == EXPECTED_YEAR
    assert res.month == EXPECTED_MONTH
    assert res.day is None
    assert res.iso == "2023-10"
