from typing import Any

import pytest
from bs4 import BeautifulSoup

from scrapers.constructors.complete_scraper import CompleteConstructorsScraper
from scrapers.constructors.helpers.export import constructor_name_initial
from scrapers.constructors.single_scraper import SingleConstructorScraper


def _make_soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


# ---------------------------------------------------------------------------
# SingleConstructorScraper - _scrape_infoboxes
# ---------------------------------------------------------------------------


def test_scrape_infoboxes_returns_empty_when_no_infobox() -> None:
    scraper = SingleConstructorScraper()
    soup = _make_soup("<div><p>No infobox here.</p></div>")
    result = scraper._scrape_infoboxes(soup)  # noqa: SLF001
    assert result == []


def test_scrape_infoboxes_finds_single_infobox() -> None:
    scraper = SingleConstructorScraper()
    soup = _make_soup(
        """
        <table class="infobox">
            <caption>Williams Racing</caption>
            <tr><th>Founded</th><td>1977</td></tr>
        </table>
        """,
    )
    result = scraper._scrape_infoboxes(soup)  # noqa: SLF001
    assert len(result) == 1
    assert result[0]["title"] == "Williams Racing"


def test_scrape_infoboxes_finds_multiple_infoboxes() -> None:
    scraper = SingleConstructorScraper()
    soup = _make_soup(
        """
        <table class="infobox"><caption>First</caption></table>
        <table class="infobox"><caption>Second</caption></table>
        """,
    )
    result = scraper._scrape_infoboxes(soup)  # noqa: SLF001
    _expected_count = 2
    assert len(result) == _expected_count


# ---------------------------------------------------------------------------
# SingleConstructorScraper - _scrape_tables
# ---------------------------------------------------------------------------


def test_scrape_tables_returns_empty_when_no_wikitable() -> None:
    scraper = SingleConstructorScraper()
    soup = _make_soup("<div><p>No tables here.</p></div>")
    result = scraper._scrape_tables(soup)  # noqa: SLF001
    assert result == []


def test_scrape_tables_extracts_headers_and_rows() -> None:
    scraper = SingleConstructorScraper()
    soup = _make_soup(
        """
        <table class="wikitable">
            <tr><th>Season</th><th>Wins</th></tr>
            <tr><td>2023</td><td>3</td></tr>
        </table>
        """,
    )
    result = scraper._scrape_tables(soup)  # noqa: SLF001
    assert len(result) == 1
    assert result[0]["headers"] == ["Season", "Wins"]
    assert result[0]["rows"] == [{"Season": "2023", "Wins": "3"}]


def test_scrape_tables_includes_caption_when_present() -> None:
    scraper = SingleConstructorScraper()
    soup = _make_soup(
        """
        <table class="wikitable">
            <caption>Race Results</caption>
            <tr><th>Year</th></tr>
            <tr><td>2022</td></tr>
        </table>
        """,
    )
    result = scraper._scrape_tables(soup)  # noqa: SLF001
    assert result[0].get("caption") == "Race Results"


def test_scrape_tables_skips_table_without_header_row() -> None:
    scraper = SingleConstructorScraper()
    soup = _make_soup('<table class="wikitable"></table>')
    result = scraper._scrape_tables(soup)  # noqa: SLF001
    assert result == []


# ---------------------------------------------------------------------------
# SingleConstructorScraper - _parse_soup
# ---------------------------------------------------------------------------


def test_parse_soup_returns_url_infoboxes_tables() -> None:
    scraper = SingleConstructorScraper()
    scraper.url = "https://en.wikipedia.org/wiki/Test"
    soup = _make_soup(
        """
        <table class="infobox"><caption>My Team</caption></table>
        <table class="wikitable">
            <tr><th>Col</th></tr>
            <tr><td>val</td></tr>
        </table>
        """,
    )
    result = scraper._parse_soup(soup)  # noqa: SLF001
    assert len(result) == 1
    record = result[0]
    assert record["url"] == "https://en.wikipedia.org/wiki/Test"
    assert "infoboxes" in record
    assert "tables" in record


# ---------------------------------------------------------------------------
# CompleteConstructorsScraper - _get_constructor_url
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("record", "expected"),
    [
        # CurrentConstructorsListScraper / FormerConstructorsListScraper style
        (
            {
                "constructor": {
                    "text": "Williams",
                    "url": "https://en.wikipedia.org/wiki/Williams",
                },
            },
            "https://en.wikipedia.org/wiki/Williams",
        ),
        # IndianapolisOnlyConstructorsListScraper style
        (
            {
                "constructor": "Kurtis Kraft",
                "constructor_url": "https://en.wikipedia.org/wiki/Kurtis_Kraft",
            },
            "https://en.wikipedia.org/wiki/Kurtis_Kraft",
        ),
        # PrivateerTeamsListScraper style
        (
            {
                "team": "BMS Scuderia Italia",
                "team_url": "https://en.wikipedia.org/wiki/BMS_Scuderia_Italia",
            },
            "https://en.wikipedia.org/wiki/BMS_Scuderia_Italia",
        ),
        # No URL available
        (
            {"constructor": "Unknown"},
            None,
        ),
        # constructor dict without url
        (
            {"constructor": {"text": "NoUrl"}},
            None,
        ),
        # Red link in constructor dict (LinkRecord style) - must be skipped
        (
            {
                "constructor": {
                    "text": "Ecurie Bleue",
                    "url": "https://en.wikipedia.org/w/index.php?title=Ecurie_Bleue&action=edit&redlink=1",
                },
            },
            None,
        ),
        # Red link as constructor_url - must be skipped
        (
            {
                "constructor": "Ecurie Bleue",
                "constructor_url": "https://en.wikipedia.org/w/index.php?title=Ecurie_Bleue&action=edit&redlink=1",
            },
            None,
        ),
        # Red link as team_url - must be skipped
        (
            {
                "team": "Ecurie Bleue",
                "team_url": "https://en.wikipedia.org/w/index.php?title=Ecurie_Bleue&action=edit&redlink=1",
            },
            None,
        ),
    ],
)
def test_get_constructor_url(record: dict[str, Any], expected: str | None) -> None:
    result = CompleteConstructorsScraper._get_constructor_url(record)  # noqa: SLF001
    assert result == expected


# ---------------------------------------------------------------------------
# constructor_name_initial helper
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("record", "expected"),
    [
        ({"constructor": {"text": "Williams Racing"}}, "W"),
        ({"constructor": {"text": "Ferrari"}}, "F"),
        ({"team": "BMS Scuderia Italia"}, "B"),
        ({"constructor": "Kurtis Kraft"}, "K"),
        ({}, "other"),
        ({"constructor": {"text": ""}}, "other"),
    ],
)
def test_constructor_name_initial(record: dict[str, Any], expected: str) -> None:
    assert constructor_name_initial(record) == expected

