# ruff: noqa: E501, PLR2004
from scrapers.columns.types.list import ListColumn
from tests.scrapers.base.table.columns.types.helpers import ctx_list


def test_list_column_empty_text_returns_empty_list() -> None:
    assert ListColumn().parse(ctx_list("")) == []


def test_list_column_none_text_returns_empty_list() -> None:
    assert ListColumn().parse(ctx_list(None)) == []


def test_list_column_single_item() -> None:
    result = ListColumn().parse(ctx_list("Ferrari"))
    assert result == ["Ferrari"]


def test_list_column_comma_separated() -> None:
    result = ListColumn().parse(ctx_list("Ferrari, McLaren"))
    assert result == ["Ferrari", "McLaren"]


def test_list_column_semicolon_separated() -> None:
    result = ListColumn().parse(ctx_list("A; B; C"))
    assert result == ["A", "B", "C"]
