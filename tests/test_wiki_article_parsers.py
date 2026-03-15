from bs4 import BeautifulSoup

from scrapers.wiki.parsers.article import CallableArticleParserAdapter
from scrapers.wiki.parsers.article import WikiParserArticleAdapter
from scrapers.wiki.parsers.header import HeaderParser
from scrapers.wiki.scraper import WikiScraper


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def test_wiki_parser_article_adapter_parses_located_tag() -> None:
    parser = WikiParserArticleAdapter(
        parser=HeaderParser(),
        locator=HeaderParser.find_header,
    )
    result = parser.parse_article(
        _soup('<header class="mw-body-header"><h1 class="mw-page-title-main">X</h1></header>'),
    )
    assert isinstance(result, dict)
    assert result["title"] == "X"


def test_wiki_scraper_registers_domain_stage_with_target_key() -> None:
    scraper = WikiScraper(include_wiki_content=False)
    scraper.url = "https://example.com"
    scraper.register_article_parser(
        CallableArticleParserAdapter(lambda _soup: [1, 2, 3]),
        target_key="domain",
    )
    result = scraper._parse_soup(_soup("<html></html>"))  # noqa: SLF001
    assert result == [{"url": "https://example.com", "domain": [1, 2, 3]}]


def test_wiki_scraper_merges_dict_when_target_key_is_none() -> None:
    scraper = WikiScraper(include_wiki_content=False)
    scraper.url = "https://example.com"
    scraper.register_article_parser(
        CallableArticleParserAdapter(lambda _soup: {"a": 1, "b": 2}),
        target_key=None,
    )
    result = scraper._parse_soup(_soup("<html></html>"))  # noqa: SLF001
    assert result == [{"url": "https://example.com", "a": 1, "b": 2}]


def test_wiki_scraper_register_wiki_parser() -> None:
    scraper = WikiScraper(include_wiki_content=False)
    scraper.url = "https://example.com"
    scraper.register_wiki_parser(
        parser=HeaderParser(),
        locator=HeaderParser.find_header,
        target_key="header",
    )
    result = scraper._parse_soup(
        _soup('<header class="mw-body-header"><h1 class="mw-page-title-main">Y</h1></header>'),
    )  # noqa: SLF001
    assert result[0]["header"]["title"] == "Y"
