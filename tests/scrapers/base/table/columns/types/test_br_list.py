from __future__ import annotations

from bs4 import BeautifulSoup

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.br_list import BrListColumn


def _ctx(
    *,
    html: str | None = None,
    clean_text: str = "",
    raw_text: str | None = None,
) -> ColumnContext:
    cell = None
    if html is not None:
        cell = BeautifulSoup(f"<td>{html}</td>", "html.parser").find("td")
    return ColumnContext(
        header="Items",
        key="items",
        raw_text=raw_text,
        clean_text=clean_text,
        links=[],
        cell=cell,
        base_url="https://en.wikipedia.org",
    )


def test_br_list_parses_single_line_text_from_cell() -> None:
    parsed = BrListColumn().parse(_ctx(html="Ferrari"))

    assert parsed == ["Ferrari"]


def test_br_list_parses_multiline_text_from_br_segments() -> None:
    parsed = BrListColumn().parse(_ctx(html="Ferrari<br>McLaren<br>Williams"))

    assert parsed == ["Ferrari", "McLaren", "Williams"]


def test_br_list_returns_empty_for_blank_content() -> None:
    parsed = BrListColumn().parse(_ctx(html="&nbsp;"))

    assert parsed == []


def test_br_list_preserves_duplicate_items() -> None:
    parsed = BrListColumn().parse(_ctx(html="Ferrari<br>Ferrari"))

    assert parsed == ["Ferrari", "Ferrari"]


def test_br_list_keeps_text_with_nonstandard_separator() -> None:
    parsed = BrListColumn().parse(_ctx(html="Ferrari | McLaren"))

    assert parsed == ["Ferrari | McLaren"]


def test_br_list_is_idempotent_for_same_context() -> None:
    column = BrListColumn()
    ctx = _ctx(html="Ferrari<br>McLaren")

    first = column.parse(ctx)
    second = column.parse(ctx)

    assert first == second == ["Ferrari", "McLaren"]
