from typing import Any

from bs4 import BeautifulSoup

from scrapers.dto import InfoboxPayloadDTO
from scrapers.dto import SectionsPayloadDTO
from scrapers.dto import TablesPayloadDTO
from scrapers.infobox.infobox.html import InfoboxHtmlParser
from scrapers.options import ScraperOptions
from scrapers.parsers.table.wiki.article import ArticleTablesParser
from scrapers.single_wiki_article.base import SingleWikiArticleScraperBase


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

    def _build_infobox_payload(self, soup: BeautifulSoup) -> InfoboxPayloadDTO:
        parser = InfoboxHtmlParser()
        infoboxes: list[dict[str, Any]] = []
        for table in self.find_infoboxes(soup):
            parsed = parser.parse_element(table)
            if parsed["title"] is not None or parsed["rows"]:
                infoboxes.append(parsed)
        return InfoboxPayloadDTO(infoboxes)

    def _build_tables_payload(self, soup: BeautifulSoup) -> TablesPayloadDTO:
        return TablesPayloadDTO(self.article_tables_parser.parse(soup))

    def _assemble_record(
        self,
        *,
        soup: BeautifulSoup,
        infobox_payload: InfoboxPayloadDTO,
        tables_payload: TablesPayloadDTO,
        sections_payload: SectionsPayloadDTO,
    ) -> dict[str, Any]:
        _ = soup, sections_payload
        return {
            "url": self.url,
            "infoboxes": infobox_payload.data,
            "tables": tables_payload.data,
        }
