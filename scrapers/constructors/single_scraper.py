from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.infobox.html_parser import InfoboxHtmlParser
from scrapers.base.options import ScraperOptions
from scrapers.wiki.scraper import WikiScraper


class SingleConstructorScraper(WikiScraper):
    """
    Scraper pojedynczego konstruktora - pobiera wszystkie infoboksy
    oraz wszystkie tabele z artykułu Wikipedii.
    """

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
    ) -> None:
        options = init_scraper_options(options, include_urls=True)
        policy = self.get_http_policy(options)
        options.with_fetcher(policy=policy)
        super().__init__(options=options)
        self.url: str = ""

    def fetch_by_url(self, url: str) -> list[dict[str, Any]]:
        self.url = url
        return super().fetch()

    def _parse_soup(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        return [
            {
                "url": self.url,
                "infoboxes": self._scrape_infoboxes(soup),
                "tables": self._scrape_tables(soup),
            },
        ]

    def _scrape_infoboxes(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        parser = InfoboxHtmlParser()
        return [parser.parse_element(table) for table in self.find_infoboxes(soup)]

    def _scrape_tables(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        tables = []
        for table in soup.find_all("table", class_="wikitable"):
            table_data = self._extract_table(table)
            if table_data:
                tables.append(table_data)
        return tables

    def _extract_table(self, table: Tag) -> dict[str, Any] | None:
        raw = self.table_parser.parse(table)
        headers = raw["headers"]
        if not headers:
            return None

        caption_tag = table.find("caption")
        caption = (
            clean_wiki_text(caption_tag.get_text(" ", strip=True))
            if caption_tag
            else None
        )

        rows = [
            dict(zip(headers, row_cells, strict=False)) for row_cells in raw["rows"]
        ]

        result: dict[str, Any] = {"headers": headers, "rows": rows}
        if caption:
            result["caption"] = caption
        return result
