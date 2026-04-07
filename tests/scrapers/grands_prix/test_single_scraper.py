# ruff: noqa: E501, PLR2004
from unittest.mock import MagicMock, patch

from bs4 import BeautifulSoup

from scrapers.grands_prix.single_scraper import F1SingleGrandPrixScraper


def _soup_without_grand_prix_markers() -> BeautifulSoup:
    return BeautifulSoup("<html><body><p>Some page</p></body></html>", "html.parser")


def _soup_with_grand_prix_markers() -> BeautifulSoup:
    # has a navbox link matching the grand prix template
    html = """
    <html><body>
    <div class="navbox"><a href="/wiki/Template:Formula_One_Grands_Prix">GP</a></div>
    </body></html>
    """
    return BeautifulSoup(html, "html.parser")


def _make_scraper() -> F1SingleGrandPrixScraper:
    from scrapers.base.options import ScraperOptions

    options = MagicMock(spec=ScraperOptions)
    options.include_urls = False
    options.normalize_empty_values = False
    options.pipeline = MagicMock()
    options.pipeline.transformers = []
    return F1SingleGrandPrixScraper.__new__(F1SingleGrandPrixScraper)


def test_parse_returns_empty_list_for_non_grand_prix_article() -> None:
    scraper = _make_scraper()
    scraper.url = "https://en.wikipedia.org/wiki/SomePage"
    scraper.include_urls = False
    scraper.normalize_empty_values = False

    with patch("scrapers.grands_prix.single_scraper.is_grand_prix_article", return_value=False):
        result = scraper.parse(_soup_without_grand_prix_markers())

    assert result == []


def test_assemble_record_returns_empty_by_year_when_parse_empty() -> None:
    scraper = _make_scraper()
    scraper.url = "https://en.wikipedia.org/wiki/SomePage"
    scraper.include_urls = False
    scraper.normalize_empty_values = False

    with patch.object(scraper, "parse", return_value=[]):
        result = scraper._assemble_record(
            soup=MagicMock(),
            infobox_payload=MagicMock(),
            tables_payload=MagicMock(),
            sections_payload=MagicMock(),
        )

    assert result == {"url": "https://en.wikipedia.org/wiki/SomePage", "by_year": []}


def test_assemble_record_returns_first_item_from_parse() -> None:
    scraper = _make_scraper()
    scraper.url = "https://en.wikipedia.org/wiki/BritishGP"
    scraper.include_urls = False
    scraper.normalize_empty_values = False

    expected = {"url": "https://en.wikipedia.org/wiki/BritishGP", "by_year": [{"year": 2023}]}
    with patch.object(scraper, "parse", return_value=[expected]):
        result = scraper._assemble_record(
            soup=MagicMock(),
            infobox_payload=MagicMock(),
            tables_payload=MagicMock(),
            sections_payload=MagicMock(),
        )

    assert result == expected
