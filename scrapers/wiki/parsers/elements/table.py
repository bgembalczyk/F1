from collections.abc import Sequence
from typing import Any

from bs4 import Tag

from scrapers.base.helpers.background import extract_background
from scrapers.base.helpers.links import normalize_links
from scrapers.base.helpers.tables.header import is_repeated_header_row
from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.table.parser import HEADER_ROWS_WITH_SUBHEADERS
from scrapers.base.table.parser import HtmlTableParser
from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.types import TableParsedData


class TableParser(WikiParser[TableParsedData]):
    """Parser tabel wikitable Wikipedii.

    Przetwarza tabelę: <table class="wikitable">
    """

    def __init__(self, table_parser: HtmlTableParser | None = None) -> None:
        self._table_parser = table_parser or HtmlTableParser()

    def parse(self, element: Tag) -> dict[str, Any]:
        """Parsuje tabelę wikitable HTML.

        Args:
            element: Element <table class="wikitable">.

        Returns:
            Słownik z nagłówkami i wierszami tabeli.
        """
        parser = self._table_parser
        full_headers, header_rows = self._extract_full_headers(parser, element)
        if not full_headers:
            return {"headers": [], "rows": [], "raw_rows": [], "rich_rows": []}

        included_indexes = [
            i for i, header in enumerate(full_headers) if header.strip()
        ]
        headers = [full_headers[i] for i in included_indexes]

        rows: list[list[str]] = []
        raw_rows: list[dict[str, str]] = []
        rich_rows: list[dict[str, Any]] = []
        pending_rowspans: dict[int, dict[str, object]] = {}

        for tr in element.find_all("tr")[header_rows:]:
            cells = tr.find_all(["td", "th"])
            if not cells or all(not c.get_text(strip=True) for c in cells):
                continue

            cleaned_cells = self._clean_cells(cells, parser)
            if parser.is_footer_row(cells, cleaned_cells, full_headers):
                continue
            if is_repeated_header_row(cleaned_cells, headers):
                continue

            expanded_cells = parser.expand_row_cells(
                cells,
                full_headers,
                pending_rowspans,
            )
            cleaned_expanded = self._clean_cells(expanded_cells, parser)

            normalized_row = [
                cleaned_expanded[idx] if idx < len(cleaned_expanded) else ""
                for idx in included_indexes
            ]
            rows.append(normalized_row)
            raw_rows.append(dict(zip(headers, normalized_row, strict=False)))

            rich_row: dict[str, Any] = {}
            for col_idx, (header, text) in enumerate(
                zip(headers, normalized_row, strict=False),
            ):
                original_idx = included_indexes[col_idx]
                cell = (
                    expanded_cells[original_idx]
                    if original_idx < len(expanded_cells)
                    else None
                )
                if cell is not None and isinstance(cell, Tag):
                    links = normalize_links(cell, drop_empty_text=True)
                    background = extract_background(cell)
                else:
                    links = []
                    background = None
                rich_row[header] = {
                    "text": text,
                    "links": links,
                    "background": background,
                }
            rich_rows.append(rich_row)

        return {
            "headers": headers,
            "rows": rows,
            "raw_rows": raw_rows,
            "rich_rows": rich_rows,
        }

    @staticmethod
    def _extract_full_headers(
        parser: HtmlTableParser,
        table: Tag,
    ) -> tuple[list[str], int]:
        table_rows = table.find_all("tr")
        if not table_rows:
            return [], 0

        first_cells = table_rows[0].find_all(["th", "td"])
        if not first_cells:
            return [], 0

        first_headers = parser.clean_cells(first_cells)

        if len(table_rows) < HEADER_ROWS_WITH_SUBHEADERS:
            return first_headers, 1

        second_cells = table_rows[1].find_all(["th", "td"])
        if not parser.has_multirow_header(first_cells, second_cells):
            return first_headers, 1

        second_headers = parser.clean_cells(second_cells)
        combined, _ = parser.combine_header_rows(
            first_cells,
            first_headers,
            second_cells,
            second_headers,
        )
        return combined, HEADER_ROWS_WITH_SUBHEADERS

    @staticmethod
    def _cleaner_config(parser: HtmlTableParser) -> dict[str, bool]:
        return {
            "strip_lang_suffix": parser.strip_lang_suffix,
            "strip_refs": parser.strip_refs,
            "normalize_dashes": parser.normalize_dashes,
        }

    @staticmethod
    def _clean_cells(
        cells: Sequence[Tag],
        parser: HtmlTableParser,
    ) -> list[str]:
        config = TableParser._cleaner_config(parser)
        return [
            clean_wiki_text(
                cell.get_text(" ", strip=True),
                strip_lang_suffix=config["strip_lang_suffix"],
                strip_refs=config["strip_refs"],
                normalize_dashes=config["normalize_dashes"],
            )
            for cell in cells
        ]
