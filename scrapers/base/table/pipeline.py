from __future__ import annotations

from typing import Any, Mapping, Sequence
from urllib.parse import urlsplit

from bs4 import BeautifulSoup, Tag

from models.records import LinkRecord
from scrapers.base.helpers.html_utils import clean_wiki_text, extract_links_from_cell
from scrapers.base.helpers.wiki import build_full_url
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.base import BaseColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.parser import HtmlTableParser
from scrapers.base.table.row import TableRow


class TablePipeline:
    """
    Pipeline parsowania tabel:
    - wybór tabeli na podstawie ScraperConfig,
    - parsowanie wierszy,
    - filtrowanie powtarzających się header-row,
    - mapowanie kolumn.
    """

    def __init__(
        self,
        *,
        config: ScraperConfig,
        include_urls: bool,
        skip_sentinel: object,
        model_fields: set[str] | None = None,
    ) -> None:
        self.config = config
        self.include_urls = include_urls
        self.base_url = config.url
        self.skip_sentinel = skip_sentinel
        self.model_fields = model_fields

        self.section_id = config.section_id
        self.expected_headers = config.expected_headers
        self.column_map = config.column_map
        self.columns = config.columns
        self.table_css_class = config.table_css_class
        self.default_column: BaseColumn = config.default_column or AutoColumn()
        self.fragment: str | None = None
        if not self.section_id:
            fragment = urlsplit(config.url).fragment
            if fragment:
                self.fragment = fragment

    def parse_soup(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        parser = HtmlTableParser(
            section_id=self.section_id,
            fragment=self.fragment,
            expected_headers=self.expected_headers,
            table_css_class=self.table_css_class,
        )

        records: list[dict[str, Any]] = []
        for row in parser.parse(soup):
            record = self.parse_cells(row.headers, row.cells)
            if record:
                records.append(record)

        return records

    def parse_row(self, row: Mapping[str, Tag]) -> dict[str, Any]:
        record: dict[str, Any] = {}

        for header, cell in row.items():
            if not isinstance(header, str):
                continue
            if header in {"__row__", "_row", "__tr__"}:
                continue
            self._apply_cell(record, header, cell)

        return record

    def parse_cells(
        self,
        headers: Sequence[str],
        cells: Sequence[Tag],
    ) -> dict[str, Any]:
        record: dict[str, Any] = {}
        for header, cell in zip(headers, cells):
            self._apply_cell(record, header, cell)
        return record

    def _normalize_cell(self, header: str, cell: Tag) -> tuple[str, str, str]:
        key = self.column_map.get(header, self.normalize_header(header))
        raw_text = cell.get_text(" ", strip=True)
        clean_text = clean_wiki_text(raw_text)
        return key, raw_text, clean_text

    def _extract_links(self, cell: Tag) -> list[LinkRecord]:
        if not self.include_urls:
            return []
        return extract_links_from_cell(
            cell,
            full_url=lambda href: build_full_url(self.base_url, href),
        )

    def _select_column(self, key: str, header: str) -> BaseColumn:
        return self.columns.get(key) or self.columns.get(header) or self.default_column

    def _apply_cell(self, record: dict[str, Any], header: str, cell: Tag) -> None:
        key, raw_text, clean_text = self._normalize_cell(header, cell)
        links = self._extract_links(cell)

        ctx = ColumnContext(
            header=header,
            key=key,
            raw_text=raw_text,
            clean_text=clean_text,
            links=links,
            cell=cell,
            skip_sentinel=self.skip_sentinel,
            model_fields=self.model_fields,
        )

        col = self._select_column(key, header)
        col.apply(ctx, record)

    @staticmethod
    def normalize_header(header: str) -> str:
        return (
            header.strip()
            .lower()
            .replace(" ", "_")
            .replace("(", "")
            .replace(")", "")
            .replace("/", "_")
        )
