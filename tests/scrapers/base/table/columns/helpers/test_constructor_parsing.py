from __future__ import annotations

import pytest
from bs4 import BeautifulSoup

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.helpers.constructor_parsing import (
    ConstructorParsingHelpers,
)

BASE_URL = "https://en.wikipedia.org"


@pytest.fixture()
def html_valid_record() -> str:
    return (
        '<td><a href="/wiki/Ferrari">Ferrari</a><br>'
        '<a href="/wiki/Mercedes-Benz_in_Formula_One">Mercedes</a></td>'
    )


@pytest.fixture()
def html_incomplete_record() -> str:
    return "<td>Ferrari -</td>"


@pytest.fixture()
def html_alias_or_text_record() -> str:
    return "<td>Scuderia Alpha - Team Beta</td>"


@pytest.fixture()
def html_links_and_no_links_record() -> tuple[str, str]:
    with_links = (
        '<td><a href="/wiki/McLaren">McLaren</a> '
        '<a href="/wiki/Ford_Motor_Company">Ford</a></td>'
    )
    without_links = "<td>Lotus - Climax</td>"
    return with_links, without_links


def ctx_from_html(html: str) -> ColumnContext:
    cell = BeautifulSoup(html, "html.parser").find("td")
    links = [
        {"text": a.get_text(strip=True), "url": f"{BASE_URL}{a.get('href')}"}
        for a in cell.find_all("a")
    ]
    text = cell.get_text(" ", strip=True)
    return ColumnContext(
        header="Constructor",
        key="constructor",
        raw_text=text,
        clean_text=text,
        links=links,
        cell=cell,
        base_url=BASE_URL,
    )


def test_split_lines_builds_two_contexts_with_expected_structure(
    html_valid_record: str,
) -> None:
    ctx = ctx_from_html(html_valid_record)

    line_contexts = ConstructorParsingHelpers.split_lines(ctx)

    assert len(line_contexts) == 2  # noqa: PLR2004
    for item in line_contexts:
        assert isinstance(item, ColumnContext)
        assert isinstance(item.links, list)
        assert isinstance(item.clean_text, str)

    assert line_contexts[0].clean_text == "Ferrari"
    assert line_contexts[0].links == [
        {"text": "Ferrari", "url": "https://en.wikipedia.org/wiki/Ferrari"},
    ]
    assert line_contexts[1].clean_text == "Mercedes"


def test_extract_part_falls_back_to_hyphen_split_when_no_links(
    html_alias_or_text_record: str,
) -> None:
    ctx = ctx_from_html(html_alias_or_text_record)

    left = ConstructorParsingHelpers.extract_part(ctx, 0)
    right = ConstructorParsingHelpers.extract_part(ctx, 1)

    assert set(left.keys()) == {"text", "url"}
    assert set(right.keys()) == {"text", "url"}
    assert left == {"text": "Scuderia Alpha", "url": None}
    assert right == {"text": "Team Beta", "url": None}


def test_extract_part_single_link_duplicates_engine_branch() -> None:
    ctx = ctx_from_html('<td><a href="/wiki/Ferrari">Ferrari</a></td>')

    chassis = ConstructorParsingHelpers.extract_part(ctx, 0)
    engine = ConstructorParsingHelpers.extract_part(ctx, 1)

    assert chassis == engine
    assert chassis is not None
    assert set(chassis.keys()) == {"text", "url"}


@pytest.mark.parametrize(
    ("record_index", "expected"),
    [
        (0, {"text": "Lotus", "url": None}),
        (1, {"text": "Climax", "url": None}),
        (2, None),
    ],
)
def test_extract_part_handles_incomplete_or_out_of_range(
    record_index: int,
    expected: dict[str, str | None] | None,
    html_links_and_no_links_record: tuple[str, str],
) -> None:
    _, no_links_html = html_links_and_no_links_record
    ctx = ctx_from_html(no_links_html)

    parsed = ConstructorParsingHelpers.extract_part(ctx, record_index)

    assert parsed == expected


def test_find_hyphen_split_index_detects_split_with_two_plus_links_before_hyphen() -> (
    None
):
    ctx = ctx_from_html(
        '<td><a href="/wiki/BRM">BRM</a> <a href="/wiki/P160">P160</a> - '
        '<a href="/wiki/Ford_Motor_Company">Ford</a></td>',
    )

    split_index = ConstructorParsingHelpers.find_hyphen_split_index(ctx)

    assert split_index == 2  # noqa: PLR2004


def test_extract_layout_text_returns_none_for_empty_and_link_only_values(
    html_incomplete_record: str,
) -> None:
    _ = html_incomplete_record

    assert ConstructorParsingHelpers.extract_layout_text("", "Ferrari") is None
    assert ConstructorParsingHelpers.extract_layout_text("Ferrari", "Ferrari") is None
