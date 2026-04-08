# ruff: noqa: E501, PLR2004
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.list import ListColumn


def ctx(clean_text: str | None) -> ColumnContext:
    return ColumnContext(
        header="Items",
        key="items",
        raw_text=clean_text,
        clean_text=clean_text,
        links=[],
        cell=None,
        base_url="https://en.wikipedia.org",
    )


def test_list_column_empty_text_returns_empty_list() -> None:
    assert ListColumn().parse(ctx("")) == []


def test_list_column_none_text_returns_empty_list() -> None:
    assert ListColumn().parse(ctx(None)) == []


def test_list_column_single_item() -> None:
    result = ListColumn().parse(ctx("Ferrari"))
    assert result == ["Ferrari"]


def test_list_column_comma_separated() -> None:
    result = ListColumn().parse(ctx("Ferrari, McLaren"))
    assert result == ["Ferrari", "McLaren"]


def test_list_column_semicolon_separated() -> None:
    result = ListColumn().parse(ctx("A; B; C"))
    assert result == ["A", "B", "C"]
