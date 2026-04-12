from __future__ import annotations

from bs4 import BeautifulSoup

from scrapers.base.table.columns.context import ColumnContext
from scrapers.columns.types.driver_rounds import DriversWithRoundsColumn


def ctx(html: str | None, links: list[dict] | None = None) -> ColumnContext:
    cell = BeautifulSoup(html, "html.parser").find("td") if html else None
    return ColumnContext(
        header="Race drivers",
        key="race_drivers",
        raw_text=None,
        clean_text=None,
        links=links or [],
        cell=cell,
        base_url="https://en.wikipedia.org",
    )


def test_parse_returns_empty_list_when_cell_is_none() -> None:
    column = DriversWithRoundsColumn()

    assert column.parse(ctx(None)) == []


def test_parse_extracts_drivers_from_br_segments_and_prefers_lookup_links() -> None:
    column = DriversWithRoundsColumn()
    context = ctx(
        "<td>"
        '<a href="/wiki/Driver_A">Driver A</a>'
        "<br/>"
        '<a href="/wiki/Driver_B">Driver B</a>'
        "</td>",
        links=[
            {"text": "Driver A", "url": "https://example.test/driver-a"},
            {"text": "Driver B", "url": "https://example.test/driver-b"},
        ],
    )

    assert column.parse(context) == [
        {"text": "Driver A", "url": "https://example.test/driver-a"},
        {"text": "Driver B", "url": "https://example.test/driver-b"},
    ]


def test_parse_skips_segments_without_links() -> None:
    column = DriversWithRoundsColumn()
    context = ctx('<td>Unknown<br/><a href="/wiki/Driver_C">Driver C</a></td>')

    # Only valid linked segments are returned.
    assert column.parse(context) == [
        {"text": "Driver C", "url": "https://en.wikipedia.org/wiki/Driver_C"},
    ]
