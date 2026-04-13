from __future__ import annotations

import pytest
from bs4 import BeautifulSoup

from scrapers.columns.helpers.driver_parsing import DriverParsingHelpers
from tests.scrapers.base.table.columns.helpers.helpers import BASE_URL
from tests.scrapers.base.table.columns.helpers.helpers import ctx_from_html_driver


def test_extract_from_context_returns_first_link_when_cell_missing(
    html_valid_record_driver: str,
) -> None:
    ctx = ctx_from_html_driver(html_valid_record_driver)
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
    html_alias_or_text_record_driver: str,
) -> None:
    segment = BeautifulSoup(html_alias_or_text_record_driver, "html.parser").find("td")

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
    html_incomplete_record_driver: str,
) -> None:
    ctx = ctx_from_html_driver(html_incomplete_record_driver)

    assert DriverParsingHelpers.extract_from_context(ctx, BASE_URL) is None


def test_links_and_no_links_fixture_paths(
    html_links_and_no_links_record_driver: tuple[str, str],
) -> None:
    html_with_links, html_without_links = html_links_and_no_links_record_driver
    ctx_with = ctx_from_html_driver(html_with_links)
    ctx_without = ctx_from_html_driver(html_without_links)

    parsed_with = DriverParsingHelpers.extract_from_context(ctx_with, BASE_URL)
    parsed_without = DriverParsingHelpers.extract_from_context(ctx_without, BASE_URL)

    assert parsed_with is not None
    assert set(parsed_with.keys()) == {"text", "url"}
    assert parsed_without is None
