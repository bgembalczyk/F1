# ruff: noqa: E501, PLR2004
import pytest

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.position import PositionColumn


def _ctx(clean_text: str | None) -> ColumnContext:
    return ColumnContext(
        header="Pos",
        key="position",
        raw_text=clean_text,
        clean_text=clean_text,
        links=[],
        cell=None,
        base_url="https://en.wikipedia.org",
    )


def test_position_column_empty_returns_none() -> None:
    assert PositionColumn().parse(_ctx("")) is None


def test_position_column_dash_returns_none() -> None:
    assert PositionColumn().parse(_ctx("-")) is None


def test_position_column_none_returns_none() -> None:
    assert PositionColumn().parse(_ctx(None)) is None


def test_position_column_integer_returns_int() -> None:
    assert PositionColumn().parse(_ctx("3")) == 3


def test_position_column_equals_returns_tied_sentinel() -> None:
    result = PositionColumn().parse(_ctx("="))
    assert result is PositionColumn.TIED


def test_position_column_non_numeric_text_returned_as_string() -> None:
    result = PositionColumn().parse(_ctx("DSQ"))
    assert result == "DSQ"


@pytest.mark.parametrize(("text", "expected"), [("1", 1), ("10", 10), ("20", 20)])
def test_position_column_various_integers(text, expected) -> None:
    assert PositionColumn().parse(_ctx(text)) == expected
