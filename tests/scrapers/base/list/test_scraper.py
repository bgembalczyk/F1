# ruff: noqa: SLF001
import pytest
from bs4 import BeautifulSoup

from scrapers.base.errors import ScraperNotFoundError
from scrapers.base.list.scraper import F1ListScraper
from scrapers.base.options import ScraperOptions


class _DummyListScraper(F1ListScraper):
    url = "https://example.com/wiki/List"
    section_id = "Drivers"
    record_key = "driver"


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def test_list_scraper_parses_section_list_fixture() -> None:
    scraper = _DummyListScraper(options=ScraperOptions(include_urls=True))
    soup = _soup(
        """
        <h2><span id="Drivers">Drivers</span></h2>
        <ul>
          <li><a href="/wiki/A"> Driver A </a></li>
          <li><a href="/wiki/B">Driver B</a></li>
        </ul>
        """,
    )

    records = scraper._parse_soup(soup)

    assert records == [
        {"driver": "Driver A", "url": "https://example.com/wiki/A"},
        {"driver": "Driver B", "url": "https://example.com/wiki/B"},
    ]


def test_list_scraper_skips_blank_item_and_handles_missing_link_cell() -> None:
    scraper = _DummyListScraper(options=ScraperOptions(include_urls=True))
    soup = _soup(
        """
        <h2><span id="Drivers">Drivers</span></h2>
        <ul>
          <li>   </li>
          <li>Driver Without Link</li>
        </ul>
        """,
    )

    records = scraper._parse_soup(soup)

    assert records == [{"driver": "Driver Without Link"}]


def test_list_scraper_raises_when_section_list_is_missing() -> None:
    scraper = _DummyListScraper(options=ScraperOptions(include_urls=False))
    soup = _soup('<h2><span id="Drivers">Drivers</span></h2><p>No list here.</p>')

    with pytest.raises(ScraperNotFoundError, match="Nie znaleziono listy w sekcji"):
        scraper._find_list_root(soup)


def test_list_scraper_requires_record_key_for_default_parse_item() -> None:
    class _NoRecordKeyScraper(F1ListScraper):
        url = "https://example.com"
        section_id = None
        record_key = None

    scraper = _NoRecordKeyScraper(options=ScraperOptions(include_urls=False))
    li = _soup("<ul><li>Example</li></ul>").find("li")
    assert li is not None

    with pytest.raises(NotImplementedError, match="record_key nie jest zdefiniowany"):
        scraper.parse_item(li)
