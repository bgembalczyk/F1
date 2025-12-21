from __future__ import annotations

from typing import Any, Callable, Mapping, Sequence

from bs4 import BeautifulSoup, Tag

from models.records import LinkRecord
from scrapers.base.helpers.wiki import clean_wiki_text, extract_links_from_cell
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.base import BaseColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.parser import HtmlTableParser


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
        full_url: Callable[[str | None], str | None],
        skip_sentinel: object,
        model_fields: set[str] | None = None,
    ) -> None:
        self.config = config
        self.include_urls = include_urls
        self.full_url = full_url
        self.skip_sentinel = skip_sentinel
        self.model_fields = model_fields

        self.section_id = config.section_id
        self.expected_headers = config.expected_headers
        self.column_map = config.column_map
        self.columns = config.columns
        self.table_css_class = config.table_css_class
        self.default_column: BaseColumn = config.default_column or AutoColumn()

    def parse_soup(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        parser = HtmlTableParser(
            section_id=self.section_id,
            expected_headers=self.expected_headers,
            table_css_class=self.table_css_class,
        )

        records: list[dict[str, Any]] = []
        for row in parser.parse(soup):
            record = self.parse_row(row)
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

    def _apply_cell(self, record: dict[str, Any], header: str, cell: Tag) -> None:
        key = self.column_map.get(header, self.normalize_header(header))

        raw_text = cell.get_text(" ", strip=True)
        clean_text = clean_wiki_text(raw_text)

        links: list[LinkRecord] = []
        if self.include_urls:
            links = extract_links_from_cell(cell, full_url=self.full_url)

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

        col = self.columns.get(key) or self.columns.get(header) or self.default_column
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
