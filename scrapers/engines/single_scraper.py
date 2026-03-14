from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.base.abc import F1Scraper
from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.infobox.html_parser import InfoboxHtmlParser
from scrapers.base.options import ScraperOptions
from scrapers.base.records import record_from_mapping
from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.dsl.column import column as dsl_column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.base.table.parser import HtmlTableParser
from scrapers.base.table.pipeline import TablePipeline


class SingleEngineManufacturerScraper(F1Scraper):
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
        for table in soup.find_all("table", class_=InfoboxHtmlParser._has_infobox_class):  # noqa: SLF001
            parsed = parser._parse_infobox(table)  # noqa: SLF001
            if parsed:
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
        headers = self._extract_headers(table)
        if not headers:
            return None

        pipeline = self._build_pipeline(headers)
        parser = HtmlTableParser()
        rows: list[dict[str, Any]] = []
        for row_index, row in enumerate(parser.parse_table(table)):
            record = pipeline.parse_cells(
                row.headers,
                row.cells,
                row_index=row_index,
            )
            if record:
                rows.append(record)

        return {"headers": headers, "rows": rows}

    def _build_pipeline(self, headers: list[str]) -> TablePipeline:
        schema = TableSchemaDSL(
            columns=[dsl_column(header, header, AutoColumn()) for header in headers],
        )
        config = ScraperConfig(
            url=self.url,
            section_id=None,
            expected_headers=None,
            schema=schema,
            default_column=AutoColumn(),
            record_factory=record_from_mapping,
        )
        return TablePipeline(
            config=config,
            include_urls=self.include_urls,
            normalize_empty_values=self.normalize_empty_values,
            debug_dir=self.debug_dir,
        )

    def _extract_headers(self, table: Tag) -> list[str]:
        header_row = table.find("tr")
        if not header_row:
            return []
        header_cells = header_row.find_all(["th", "td"])
        return [clean_wiki_text(c.get_text(" ", strip=True)) for c in header_cells]
