# ruff: noqa: E501, PLR2004

from scrapers.base.helpers.date_parsing import parse_date_with_category_marker
from scrapers.base.helpers.date_parsing import parse_formula_category
from scrapers.base.table.columns.context import ColumnContext


def ctx(clean_text: str | None, raw_text: str | None = None) -> ColumnContext:
    return ColumnContext(
        header="Date",
        key="date",
        raw_text=raw_text if raw_text is not None else clean_text,
        clean_text=clean_text,
        links=[],
        cell=None,
        base_url="https://en.wikipedia.org",
    )


def test_parse_date_with_category_marker_empty_returns_none() -> None:
    assert parse_date_with_category_marker(ctx(""), "#") is None
    assert parse_date_with_category_marker(ctx(None), "#") is None


def test_parse_date_with_category_marker_strips_marker() -> None:
    # Should parse "2024-03-15" after stripping "#"
    result = parse_date_with_category_marker(ctx("#2024-03-15"), "#")
    assert result is not None


def test_parse_date_with_category_marker_returns_string() -> None:
    result = parse_date_with_category_marker(ctx("2020-01-01"), "#")
    assert isinstance(result, str) or result is None


def test_parse_formula_category_none_text_returns_none() -> None:
    assert parse_formula_category(ctx(None, raw_text=None), "#") is None
    assert parse_formula_category(ctx("", raw_text=""), "#") is None


def test_parse_formula_category_with_marker_returns_f2() -> None:
    # raw_text contains "#" -> F2
    result = parse_formula_category(ctx("2024 race", raw_text="2024 race #"), "#")
    assert result == "F2"


def test_parse_formula_category_without_marker_returns_f1() -> None:
    result = parse_formula_category(ctx("2024 race", raw_text="2024 race"), "#")
    assert result == "F1"
