"""Tests for DateRangeColumn (seasons/columns/date_range.py)."""

from __future__ import annotations

from scrapers.base.table.columns.context import ColumnContext
from scrapers.seasons.columns.date_range import DateRangeColumn


def _ctx(text: str | None) -> ColumnContext:
    return ColumnContext(
        header="Date",
        key="date",
        raw_text=text,
        clean_text=text or "",
        links=[],
        cell=None,
        base_url="https://en.wikipedia.org",
    )


def test_date_range_returns_none_for_empty_text() -> None:
    column = DateRangeColumn(year=2023)
    assert column.parse(_ctx("")) is None
    assert column.parse(_ctx(None)) is None


def test_date_range_parses_day_range_with_trailing_month() -> None:
    column = DateRangeColumn(year=2023)
    result = column.parse(_ctx("15-17 March"))
    assert result is not None
    assert result["start"].iso == "2023-03-15"
    assert result["end"].iso == "2023-03-17"


def test_date_range_parses_full_date_range() -> None:
    column = DateRangeColumn(year=2023)
    result = column.parse(_ctx("28 April - 1 May"))
    assert result is not None
    assert result["start"].iso == "2023-04-28"
    assert result["end"].iso == "2023-05-01"


def test_date_range_single_date_returns_same_start_and_end() -> None:
    column = DateRangeColumn(year=2023)
    result = column.parse(_ctx("15 March"))
    assert result is not None
    assert result["start"].iso == result["end"].iso
    assert result["start"].iso == "2023-03-15"


def test_date_range_uses_year_from_constructor() -> None:
    column = DateRangeColumn(year=1990)
    result = column.parse(_ctx("10-12 May"))
    assert result is not None
    assert result["start"].iso == "1990-05-10"
    assert result["end"].iso == "1990-05-12"


def test_date_range_unparseable_text_returns_result_with_none_iso() -> None:
    column = DateRangeColumn(year=2023)
    result = column.parse(_ctx("not a date at all xyz"))
    # DateRangeColumn does not return None for unparseable text;
    # it returns a dict with NormalizedDate having iso=None.
    assert result is not None
    assert result["start"].iso is None
    assert result["end"].iso is None
