from __future__ import annotations

import math

import pytest
from bs4 import BeautifulSoup

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.helpers.results_parsing import ResultsParsingHelpers

BASE_URL = "https://en.wikipedia.org"


@pytest.fixture()
def html_valid_record() -> str:
    return (
        '<td><a href="/wiki/Scuderia_Ferrari">Scuderia Ferrari</a>'
        "<sup>12</sup><sup>†</sup><sup>*</sup></td>"
    )


@pytest.fixture()
def html_incomplete_record() -> str:
    return "<td></td>"


@pytest.fixture()
def html_alias_or_text_record() -> str:
    return "<td>half points awarded</td>"


@pytest.fixture()
def html_links_and_no_links_record() -> tuple[str, str]:
    return (
        '<td><a href="/wiki/Team_Lotus">Team Lotus</a></td>',
        "<td>No sponsors listed</td>",
    )


def _ctx_from_html(html: str) -> ColumnContext:
    cell = BeautifulSoup(html, "html.parser").find("td")
    links = [
        {"text": a.get_text(strip=True), "url": f"{BASE_URL}{a.get('href')}"}
        for a in cell.find_all("a")
    ]
    text = cell.get_text(" ", strip=True)
    return ColumnContext(
        header="Results",
        key="results",
        raw_text=text,
        clean_text=text,
        links=links,
        cell=cell,
        base_url=BASE_URL,
    )


@pytest.mark.parametrize(
    ("branch_id", "text", "expected"),
    [
        ("70->72", "57 1/7", 57 + (1 / 7)),
        ("72->75", "1/2", 0.5),
        ("77->78", "12.5", 12.5),
    ],
)
def test_parse_points_value_branch_coverage(
    branch_id: str,
    text: str,
    expected: float,
) -> None:
    _ = branch_id
    value = ResultsParsingHelpers.parse_points_value(text)

    assert isinstance(value, float)
    assert math.isclose(value, expected, rel_tol=1e-9)


def test_parse_points_value_returns_none_on_alias_text(
    html_alias_or_text_record: str,
) -> None:
    text = (
        BeautifulSoup(html_alias_or_text_record, "html.parser")
        .find("td")
        .get_text(
            " ",
            strip=True,
        )
    )

    assert ResultsParsingHelpers.parse_points_value(text) is None


def test_parse_results_structure_for_mixed_values() -> None:
    parsed = ResultsParsingHelpers.parse_results("1st/Ret/DNS")

    assert isinstance(parsed, list)
    assert len(parsed) == 3  # noqa: PLR2004
    assert all(isinstance(item, dict) for item in parsed)
    assert parsed[0].keys() == {"position", "status"}
    assert isinstance(parsed[0]["position"], int)
    assert isinstance(parsed[0]["status"], str)
    assert parsed[1] == {"status": "retired"}
    assert parsed[2] == {"status": "did_not_start"}


@pytest.mark.parametrize(
    ("token", "expected_status"),
    [
        ("DNQ", "did_not_qualify"),
        ("DSQ", "disqualified"),
        ("NC", "not_classified"),
        ("OtherText", "othertext"),
    ],
)
def test_parse_result_part_status_map_and_fallback(
    token: str,
    expected_status: str,
) -> None:
    parsed = ResultsParsingHelpers._parse_result_part(token)  # noqa: SLF001

    assert isinstance(parsed, dict)
    assert set(parsed.keys()) == {"status"}
    assert isinstance(parsed["status"], str)
    assert parsed["status"] == expected_status


def test_parse_superscripts_returns_expected_tuple_structure(
    html_valid_record: str,
) -> None:
    ctx = _ctx_from_html(html_valid_record)

    reference_number, has_dagger, has_asterisk = (
        ResultsParsingHelpers.parse_superscripts(
            ctx,
        )
    )

    assert isinstance(reference_number, int)
    assert isinstance(has_dagger, bool)
    assert isinstance(has_asterisk, bool)
    assert (reference_number, has_dagger, has_asterisk) == (12, True, True)


def test_parse_superscripts_fallback_for_missing_cell(
    html_incomplete_record: str,
) -> None:
    ctx = _ctx_from_html(html_incomplete_record)
    ctx.cell = None

    assert ResultsParsingHelpers.parse_superscripts(ctx) == (None, False, False)


def test_parse_entrant_segment_with_and_without_links(
    html_links_and_no_links_record: tuple[str, str],
) -> None:
    with_links_html, without_links_html = html_links_and_no_links_record
    with_links_segment = BeautifulSoup(with_links_html, "html.parser").find("td")
    without_links_segment = BeautifulSoup(without_links_html, "html.parser").find("td")

    parsed_with = ResultsParsingHelpers.parse_entrant_segment(
        with_links_segment,
        {},
        BASE_URL,
    )
    parsed_without = ResultsParsingHelpers.parse_entrant_segment(
        without_links_segment,
        {},
        BASE_URL,
    )

    for parsed in (parsed_with, parsed_without):
        assert set(parsed.keys()) == {"name", "title_sponsors"}
        assert isinstance(parsed["name"], str)
        assert isinstance(parsed["title_sponsors"], list)

    assert parsed_with["title_sponsors"] == [
        {"text": "Team Lotus", "url": "https://en.wikipedia.org/wiki/Team_Lotus"},
    ]
    assert parsed_without["title_sponsors"] == []


def test_extract_licenses_and_fallback_empty_segments() -> None:
    segments = [
        BeautifulSoup('<td><a href="/wiki/UK">UK</a></td>', "html.parser").find("td"),
        BeautifulSoup("<td>No link</td>", "html.parser").find("td"),
    ]

    parsed = ResultsParsingHelpers.extract_licenses(segments, BASE_URL)

    assert isinstance(parsed, list)
    assert parsed == [{"text": "UK", "url": "https://en.wikipedia.org/wiki/UK"}]


def test_strip_refs_removes_all_sup_tags() -> None:
    segment = BeautifulSoup(
        "<td>1st<sup>1</sup><sup>†</sup></td>",
        "html.parser",
    ).find("td")

    ResultsParsingHelpers.strip_refs(segment)

    assert segment.find("sup") is None
    assert segment.get_text("", strip=True) == "1st"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Car #22", 22),
        ("No numeric value", None),
        ("", None),
    ],
)
def test_extract_number_paths(text: str, expected: int | None) -> None:
    assert ResultsParsingHelpers.extract_number(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Season 1999", True),
        ("held in 2099", True),
        ("1700", False),
        ("", False),
    ],
)
def test_has_year_paths(text: str, expected: bool) -> None:  # noqa: FBT001
    assert ResultsParsingHelpers.has_year(text) is expected
