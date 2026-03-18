from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.infobox.html_parser import InfoboxHtmlParser
from scrapers.base.options import ScraperOptions
from scrapers.base.single_wiki_article import SingleWikiArticleScraperBase
from scrapers.wiki.parsers.elements.article_tables import ArticleTablesParser


class SingleEngineManufacturerScraper(SingleWikiArticleScraperBase):
    """
    Scraper pojedynczego producenta silnika - pobiera wszystkie infoboksy
    oraz wszystkie tabele z artykułu Wikipedii.
    """

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
    ) -> None:
        super().__init__(options=options)
        self.article_tables_parser = ArticleTablesParser()

    def _build_infobox_payload(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        parser = InfoboxHtmlParser()
        infoboxes: list[dict[str, Any]] = []
        for table in self.find_infoboxes(soup):
            parsed = parser.parse_element(table)
            if parsed["title"] is not None or parsed["rows"]:
                infoboxes.append(parsed)
        return infoboxes

    def _build_tables_payload(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        return self.article_tables_parser.parse(soup)

    def _assemble_record(
        self,
        *,
        soup: BeautifulSoup,
        infobox_payload: list[dict[str, Any]],
        tables_payload: list[dict[str, Any]],
        sections_payload: list[dict[str, Any]],
    ) -> dict[str, Any]:
        _ = soup, sections_payload
        return {
            "url": self.url,
            "infoboxes": infobox_payload,
            "tables": tables_payload,
        }
