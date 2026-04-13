import pytest
from bs4 import BeautifulSoup

from scrapers.errors.not_found import ScraperNotFoundError
from scrapers.options import ScraperOptions
from tests.scrapers.base.list.dummy_classes import DummyListScraper
from tests.scrapers.base.list.helpers import soup_func
from scrapers.list.base import F1ListScraper


def test_list_scraper_parses_section_list_fixture() -> None:
    scraper = DummyListScraper(options=ScraperOptions(include_urls=True))
    soup = soup_func(
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
    scraper = DummyListScraper(options=ScraperOptions(include_urls=True))
    soup = soup_func(
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
    scraper = DummyListScraper(options=ScraperOptions(include_urls=False))
    soup = soup_func('<h2><span id="Drivers">Drivers</span></h2><p>No list here.</p>')

    with pytest.raises(ScraperNotFoundError, match="Nie znaleziono listy w sekcji"):
        scraper._find_list_root(soup)


def test_list_scraper_requires_record_key_for_default_parse_item() -> None:
    class _NoRecordKeyScraper(F1ListScraper):
        url = "https://example.com"
        section_id = None
        record_key = None

    scraper = _NoRecordKeyScraper(options=ScraperOptions(include_urls=False))
    li = soup_func("<ul><li>Example</li></ul>").find("li")
    assert li is not None

    with pytest.raises(NotImplementedError, match="record_key nie jest zdefiniowany"):
        scraper.parse_item(li)
