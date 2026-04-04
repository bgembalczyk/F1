"""Regression tests for DriverParsingHelpers."""

from scrapers.base.table.columns.helpers.driver_parsing import DriverParsingHelpers

EXPECTED_LEWIS_HAMILTON_LINKS = 2


def test_build_link_lookup_handles_link_list_without_recursion() -> None:
    """`build_link_lookup` should delegate to shared helper, not recurse."""
    links = [
        {
            "text": "Lewis Hamilton",
            "url": "https://en.wikipedia.org/wiki/Lewis_Hamilton",
        },
        {
            "text": "LEWIS HAMILTON",
            "url": "https://en.wikipedia.org/wiki/Lewis_Hamilton",
        },
    ]

    lookup = DriverParsingHelpers.build_link_lookup(links)

    assert "lewis hamilton" in lookup
    assert len(lookup["lewis hamilton"]) == EXPECTED_LEWIS_HAMILTON_LINKS
