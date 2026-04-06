from __future__ import annotations

from scrapers.base.table.columns.context import ColumnContext
from scrapers.points.columns.first_place import FirstPlaceColumn


def _ctx(clean_text: str) -> ColumnContext:
    return ColumnContext(
        header="1st",
        key="first_place",
        raw_text=clean_text,
        clean_text=clean_text,
        links=[],
        cell=None,
        base_url="https://example.com",
    )


def test_first_place_returns_plain_int_without_role_suffix() -> None:
    assert FirstPlaceColumn().parse(_ctx("25")) == 25


def test_first_place_returns_driver_role_payload() -> None:
    assert FirstPlaceColumn().parse(_ctx("8 (D)")) == {"value": 8, "role": "driver"}


def test_first_place_returns_constructor_role_payload_case_insensitive() -> None:
    assert FirstPlaceColumn().parse(_ctx("10 (c)")) == {
        "value": 10,
        "role": "constructor",
    }


def test_first_place_returns_none_for_non_numeric_content() -> None:
    assert FirstPlaceColumn().parse(_ctx("n/a")) is None
