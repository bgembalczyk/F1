from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.infobox.html_parser import InfoboxHtmlParser
from scrapers.base.options import ScraperOptions
from scrapers.wiki.scraper import WikiScraper

_HAS_INFOBOX_CLASS = InfoboxHtmlParser._has_infobox_class  # noqa: SLF001


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
        return [
            parser._parse_infobox(table)  # noqa: SLF001
            for table in soup.find_all("table", class_=_HAS_INFOBOX_CLASS)
        ]

    def _scrape_tables(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        tables = []
        for table in soup.find_all("table", class_="wikitable"):
            table_data = self._extract_table(table)
            if table_data:
                tables.append(table_data)
        return tables

    def _extract_table(self, table: Tag) -> dict[str, Any] | None:
        header_row = table.find("tr")
        if not header_row:
            return None

        header_cells = header_row.find_all(["th", "td"])
        headers = [clean_wiki_text(c.get_text(" ", strip=True)) for c in header_cells]
        if not headers:
            return None

        caption_tag = table.find("caption")
        caption = (
            clean_wiki_text(caption_tag.get_text(" ", strip=True))
            if caption_tag
            else None
        )

        rows = []
        for tr in table.find_all("tr")[1:]:
            cells = tr.find_all(["td", "th"])
            if not cells:
                continue
            cell_texts = [clean_wiki_text(c.get_text(" ", strip=True)) for c in cells]
            if not any(cell_texts):
                continue
            row = dict(zip(headers, cell_texts, strict=False))
            rows.append(row)

        result: dict[str, Any] = {"headers": headers, "rows": rows}
        if caption:
            result["caption"] = caption
        return result
