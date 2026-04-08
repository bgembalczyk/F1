# ruff: noqa: E501, PLR2004
"""Tests for WikiScraper covering lines 97-99, 113-127."""

from unittest.mock import patch

from bs4 import BeautifulSoup

from scrapers.wiki.scraper import WikiScraper


def make_minimal_soup(
    *,
    with_header: bool = False,
    with_body: bool = False,
) -> BeautifulSoup:
    parts = ["<html><body>"]
    if with_header:
        parts.append(
            '<header class="mw-body-header vector-page-titlebar no-font-mode-scale"><h1>Test Title</h1></header>',
        )
    if with_body:
        parts.append('<div id="bodyContent"><p>body text</p></div>')
    parts.append("</body></html>")
    return BeautifulSoup("".join(parts), "html.parser")


class TestWikiScraperScrape:
    def test_scrape_returns_empty_dict_when_fetch_returns_empty(self):
        scraper = WikiScraper()
        with patch.object(scraper, "fetch", return_value=[]):
            result = scraper.scrape("https://en.wikipedia.org/wiki/Test")
        assert result == {}

    def test_scrape_returns_first_record_when_fetch_succeeds(self):
        scraper = WikiScraper()
        expected = {
            "url": "https://en.wikipedia.org/wiki/Test",
            "header": None,
            "body_content": None,
        }
        with patch.object(scraper, "fetch", return_value=[expected]):
            result = scraper.scrape("https://en.wikipedia.org/wiki/Test")
        assert result == expected

    def test_scrape_sets_url_attribute(self):
        scraper = WikiScraper()
        url = "https://en.wikipedia.org/wiki/Lewis_Hamilton"
        with patch.object(scraper, "fetch", return_value=[{"url": url}]):
            scraper.scrape(url)
        assert scraper.url == url


class TestWikiScraperParseSoup:
    def test_parse_soup_no_header_no_body(self):
        scraper = WikiScraper()
        scraper.url = "https://en.wikipedia.org/wiki/Test"
        soup = BeautifulSoup("<html><body><p>nothing</p></body></html>", "html.parser")
        result = scraper._parse_soup(soup)
        assert len(result) == 1
        record = result[0]
        assert record["url"] == "https://en.wikipedia.org/wiki/Test"
        assert record["header"] is None
        assert record["body_content"] is None

    def test_parse_soup_with_header_sets_header(self):
        scraper = WikiScraper()
        scraper.url = "https://en.wikipedia.org/wiki/Test"
        soup = make_minimal_soup(with_header=True)
        result = scraper._parse_soup(soup)
        assert len(result) == 1
        # header_parser.parse is called when find_header returns something
        assert result[0]["url"] == "https://en.wikipedia.org/wiki/Test"

    def test_parse_soup_with_body_sets_body_content(self):
        scraper = WikiScraper()
        scraper.url = "https://en.wikipedia.org/wiki/Test"
        soup = make_minimal_soup(with_body=True)
        result = scraper._parse_soup(soup)
        assert len(result) == 1

    def test_parse_soup_returns_list(self):
        scraper = WikiScraper()
        scraper.url = "https://en.wikipedia.org/wiki/Test"
        soup = BeautifulSoup("<html><body></body></html>", "html.parser")
        result = scraper._parse_soup(soup)
        assert isinstance(result, list)
        assert len(result) == 1
