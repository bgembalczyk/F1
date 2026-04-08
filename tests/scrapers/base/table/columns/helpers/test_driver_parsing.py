from __future__ import annotations

import pytest
from bs4 import BeautifulSoup

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.helpers.driver_parsing import DriverParsingHelpers

BASE_URL = "https://en.wikipedia.org"


@pytest.fixture()
def html_valid_record() -> str:
    return '<td><a href="/wiki/Lewis_Hamilton">Lewis Hamilton</a></td>'


@pytest.fixture()
def html_incomplete_record() -> str:
    return "<td>Unknown driver</td>"


@pytest.fixture()
def html_alias_or_text_record() -> str:
    return '<td><a href="/wiki/Lewis_Hamilton">Sir Lewis Hamilton</a></td>'


@pytest.fixture()
def html_links_and_no_links_record() -> tuple[str, str]:
    return (
        '<td><a href="/wiki/Max_Verstappen">Max Verstappen</a></td>',
        "<td>Reserve entry</td>",
    )


def ctx_from_html(html: str) -> ColumnContext:
    cell = BeautifulSoup(html, "html.parser").find("td")
    links = [
        {"text": a.get_text(strip=True), "url": f"{BASE_URL}{a.get('href')}"}
        for a in cell.find_all("a")
    ]
    text = cell.get_text(" ", strip=True)
    return ColumnContext(
        header="Driver",
        key="driver",
        raw_text=text,
        clean_text=text,
        links=links,
        cell=cell,
        base_url=BASE_URL,
    )


def test_extract_from_context_returns_first_link_when_cell_missing(
    html_valid_record: str,
) -> None:
    ctx = ctx_from_html(html_valid_record)
    ctx.cell = None

    parsed = DriverParsingHelpers.extract_from_context(ctx, BASE_URL)

    assert parsed is not None
    assert set(parsed.keys()) == {"text", "url"}
    assert isinstance(parsed["text"], str)
    assert isinstance(parsed["url"], str)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Round 5-7", "Round 5-7"),
        ("round 9", "round 9"),
        ("", None),
        ("Driver only", None),
    ],
)
def test_extract_rounds_text_branches(text: str, expected: str | None) -> None:
    assert DriverParsingHelpers.extract_rounds_text(text) == expected


def test_strip_rounds_and_number_removes_both_prefixes() -> None:
    assert DriverParsingHelpers.strip_rounds_and_number("Round #44 Lewis Hamilton") == (
        "Lewis Hamilton"
    )


def test_parse_segment_fallback_returns_segment_link_when_lookup_misses_alias(
    html_alias_or_text_record: str,
) -> None:
    segment = BeautifulSoup(html_alias_or_text_record, "html.parser").find("td")

    parsed = DriverParsingHelpers.parse_segment(
        segment,
        {
            "lewis hamilton": [
                {"text": "Lewis Hamilton", "url": f"{BASE_URL}/wiki/Lewis_Hamilton"},
            ],
        },
        BASE_URL,
    )

    assert parsed == {
        "text": "Sir Lewis Hamilton",
        "url": "https://en.wikipedia.org/wiki/Lewis_Hamilton",
    }


def test_extract_from_context_returns_none_for_incomplete_record(
    html_incomplete_record: str,
) -> None:
    ctx = ctx_from_html(html_incomplete_record)

    assert DriverParsingHelpers.extract_from_context(ctx, BASE_URL) is None


def test_links_and_no_links_fixture_paths(
    html_links_and_no_links_record: tuple[str, str],
) -> None:
    html_with_links, html_without_links = html_links_and_no_links_record
    ctx_with = ctx_from_html(html_with_links)
    ctx_without = ctx_from_html(html_without_links)

    parsed_with = DriverParsingHelpers.extract_from_context(ctx_with, BASE_URL)
    parsed_without = DriverParsingHelpers.extract_from_context(ctx_without, BASE_URL)

    assert parsed_with is not None
    assert set(parsed_with.keys()) == {"text", "url"}
    assert parsed_without is None
