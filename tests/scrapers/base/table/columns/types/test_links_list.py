from __future__ import annotations

import pytest
from bs4 import BeautifulSoup

from scrapers.base.table.columns.context import ColumnContext
from scrapers.columns.types.links_list import LinksListColumn


def ctx(
    *,
    clean_text: str,
    links: list[dict[str, str | None]] | None = None,
    html: str | None = None,
) -> ColumnContext:
    cell = None
    if html is not None:
        cell = BeautifulSoup(f"<td>{html}</td>", "html.parser").find("td")
    return ColumnContext(
        header="Links",
        key="links",
        raw_text=clean_text,
        clean_text=clean_text,
        links=links or [],
        cell=cell,
        base_url="https://en.wikipedia.org",
    )


def test_links_list_returns_normalized_valid_links() -> None:
    parsed = LinksListColumn().parse(
        ctx(
            clean_text="Ferrari, McLaren",
            links=[
                {"text": "Ferrari*", "url": "/wiki/Ferrari"},
                {"text": "McLaren", "url": "/wiki/McLaren"},
            ],
        ),
    )

    assert parsed == [
        {"text": "Ferrari", "url": "/wiki/Ferrari"},
        {"text": "McLaren", "url": "/wiki/McLaren"},
    ]


def test_links_list_raises_for_broken_link_url() -> None:
    with pytest.raises(ValueError, match="nieprawidłowy URL"):
        LinksListColumn().parse(
            ctx(
                clean_text="Broken",
                links=[{"text": "Broken", "url": "bad url"}],
            ),
        )


def test_links_list_keeps_missing_href_entries() -> None:
    parsed = LinksListColumn().parse(
        ctx(
            clean_text="Ferrari, NoHref",
            links=[
                {"text": "Ferrari", "url": "/wiki/Ferrari"},
                {"text": "NoHref", "url": None},
            ],
        ),
    )

    assert parsed == [
        {"text": "Ferrari", "url": "/wiki/Ferrari"},
        {"text": "NoHref", "url": None},
    ]


def test_links_list_supports_mixed_content_text_and_link_items() -> None:
    parsed = LinksListColumn(text_for_missing_url=True).parse(
        ctx(
            clean_text="Factory, Ferrari, Customer",
            html="Factory, <a href='/wiki/Ferrari'>Ferrari</a>, Customer",
            links=[{"text": "Ferrari", "url": "/wiki/Ferrari"}],
        ),
    )

    assert parsed == [
        "Factory",
        {"text": "Ferrari", "url": "/wiki/Ferrari"},
        "Customer",
    ]


def test_links_list_preserves_duplicate_elements_and_links() -> None:
    parsed = LinksListColumn(text_for_missing_url=True).parse(
        ctx(
            clean_text="Ferrari, Ferrari",
            html=(
                "<a href='/wiki/Ferrari'>Ferrari</a>"
                ", Ferrari, "
                "<a href='/wiki/Ferrari'>Ferrari</a>"
            ),
            links=[
                {"text": "Ferrari", "url": "/wiki/Ferrari"},
                {"text": "Ferrari", "url": "/wiki/Ferrari"},
            ],
        ),
    )

    assert parsed == [
        {"text": "Ferrari", "url": "/wiki/Ferrari"},
        "Ferrari",
        {"text": "Ferrari", "url": "/wiki/Ferrari"},
    ]


def test_links_list_handles_nonstandard_separator_as_single_text_item() -> None:
    parsed = LinksListColumn(text_for_missing_url=True).parse(
        ctx(clean_text="Ferrari | McLaren", html="Ferrari | McLaren"),
    )

    assert parsed == ["Ferrari | McLaren"]


def test_links_list_returns_empty_for_blank_value() -> None:
    parsed = LinksListColumn(text_for_missing_url=True).parse(
        ctx(clean_text="", html="&nbsp;"),
    )

    assert parsed == []


def test_links_list_is_idempotent_for_same_context() -> None:
    column = LinksListColumn(text_for_missing_url=True)
    context = ctx(
        clean_text="Ferrari, Customer",
        html="<a href='/wiki/Ferrari'>Ferrari</a>, Customer",
        links=[{"text": "Ferrari", "url": "/wiki/Ferrari"}],
    )

    first = column.parse(context)
    second = column.parse(context)

    assert first == second == [{"text": "Ferrari", "url": "/wiki/Ferrari"}, "Customer"]
