# ruff: noqa: E501, PLR2004
import pytest

from scrapers.columns.types.position import PositionColumn
from tests.scrapers.base.table.columns.types.helpers import ctx_position


def test_position_column_empty_returns_none() -> None:
    assert PositionColumn().parse(ctx_position("")) is None


def test_position_column_dash_returns_none() -> None:
    assert PositionColumn().parse(ctx_position("-")) is None


def test_position_column_none_returns_none() -> None:
    assert PositionColumn().parse(ctx_position(None)) is None


def test_position_column_integer_returns_int() -> None:
    assert PositionColumn().parse(ctx_position("3")) == 3


def test_position_column_equals_returns_tied_sentinel() -> None:
    result = PositionColumn().parse(ctx_position("="))
    assert result is PositionColumn.TIED


def test_position_column_non_numeric_text_returned_as_string() -> None:
    result = PositionColumn().parse(ctx_position("DSQ"))
    assert result == "DSQ"


@pytest.mark.parametrize(("text", "expected"), [("1", 1), ("10", 10), ("20", 20)])
def test_position_column_various_integers(text, expected) -> None:
    assert PositionColumn().parse(ctx_position(text)) == expected
