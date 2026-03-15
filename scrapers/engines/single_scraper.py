from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.infobox.html_parser import InfoboxHtmlParser
from scrapers.base.options import ScraperOptions
from scrapers.wiki.scraper import WikiScraper


class SingleEngineManufacturerScraper(WikiScraper):
    """
    Scraper pojedynczego producenta silnika - pobiera wszystkie infoboksy
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
        self.policy = self.http_policy
        self.url: str = ""
        self.debug_dir = options.debug_dir

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
        infoboxes: list[dict[str, Any]] = []
        for table in soup.find_all("table", class_=InfoboxHtmlParser.has_infobox_class):
            parsed = parser.parse_element(table)
            if parsed["title"] is not None or parsed["rows"]:
                infoboxes.append(parsed)
        return infoboxes

    def _scrape_tables(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        all_tables: list[dict[str, Any]] = []
        for table in soup.find_all("table", class_="wikitable"):
            parsed = self._parse_table(table)
            if parsed is not None:
                all_tables.append(parsed)
        return all_tables

    def _parse_table(self, table: Tag) -> dict[str, Any] | None:
        raw = self.table_parser.parse(table)
        headers = raw["headers"]
        if not headers:
            return None
        rows = [dict(zip(headers, row_cells, strict=False)) for row_cells in raw["rows"]]
        return {"headers": headers, "rows": rows}
