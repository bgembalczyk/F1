import logging
from typing import Optional, Sequence

from bs4 import BeautifulSoup, Tag

from scrapers.base.helpers.html_utils import find_section_elements
from scrapers.base.helpers.tables.header import is_repeated_header_row
from scrapers.base.helpers.text_normalization import clean_wiki_text
from scrapers.base.table.headers import normalize_header
from scrapers.base.table.row import TableRow

logger = logging.getLogger(__name__)


class HtmlTableParser:
    """
    Parser tabel HTML, który zwraca listę wierszy jako mapowania
    nagłówków na komórki.
    """

    def __init__(
        self,
        *,
        section_id: Optional[str] = None,
        fragment: Optional[str] = None,
        expected_headers: Sequence[str] | None = None,
        table_css_class: str = "wikitable",
        strip_lang_suffix: bool = True,
        strip_refs: bool = True,
        normalize_dashes: bool = True,
    ) -> None:
        self.section_id = section_id
        self.fragment = fragment
        self.expected_headers = expected_headers
        self.table_css_class = table_css_class
        self.strip_lang_suffix = strip_lang_suffix
        self.strip_refs = strip_refs
        self.normalize_dashes = normalize_dashes

    def parse(self, soup: BeautifulSoup) -> list[TableRow]:
        table = self._find_table(soup)
        header_row = table.find("tr")
        if not header_row:
            raise RuntimeError("Nie znaleziono wiersza nagłówkowego w tabeli.")

        header_cells = header_row.find_all(["th", "td"])
        headers = [
            clean_wiki_text(
                c.get_text(" ", strip=True),
                strip_lang_suffix=self.strip_lang_suffix,
                strip_refs=self.strip_refs,
                normalize_dashes=self.normalize_dashes,
            )
            for c in header_cells
        ]

        records: list[TableRow] = []
        pending_rowspans: dict[int, dict[str, object]] = {}
        for tr in table.find_all("tr")[1:]:
            cells = tr.find_all(["td", "th"])

            if not cells or all(not c.get_text(strip=True) for c in cells):
                continue

            cleaned_cells = [
                clean_wiki_text(
                    c.get_text(" ", strip=True),
                    strip_lang_suffix=self.strip_lang_suffix,
                    strip_refs=self.strip_refs,
                    normalize_dashes=self.normalize_dashes,
                )
                for c in cells
            ]
            if self._is_footer_row(cells, cleaned_cells, headers):
                logger.debug("Pomijam wiersz stopki w tabeli.")
                continue
            if is_repeated_header_row(cleaned_cells, headers):
                logger.debug("Pomijam powtórzony wiersz nagłówka w tabeli.")
                continue

            if cells:
                expanded_cells = self._expand_row_cells(
                    cells,
                    headers,
                    pending_rowspans,
                )
                records.append(
                    TableRow(headers=headers, cells=expanded_cells, raw_tr=tr)
                )

        return records

    def _find_table(self, soup: BeautifulSoup) -> Tag:
        section_id = self.section_id or self._normalize_fragment(self.fragment)
        candidate_tables = find_section_elements(
            soup, section_id, ["table"], class_=self.table_css_class
        )

        for table in candidate_tables:
            header_row = table.find("tr")
            if not header_row:
                continue
            header_cells = header_row.find_all(["th", "td"])
            headers = [
                clean_wiki_text(
                    c.get_text(" ", strip=True),
                    strip_lang_suffix=self.strip_lang_suffix,
                    strip_refs=self.strip_refs,
                    normalize_dashes=self.normalize_dashes,
                )
                for c in header_cells
            ]

            if self._headers_match(headers):
                return table

        raise RuntimeError("Nie znaleziono pasującej tabeli.")

    def _headers_match(self, headers: Sequence[str]) -> bool:
        if not self.expected_headers:
            return True

        header_set = {normalize_header(h) for h in headers}
        expected = {normalize_header(h) for h in self.expected_headers}
        return all(h in header_set for h in expected)

    @staticmethod
    def _normalize_fragment(fragment: Optional[str]) -> Optional[str]:
        if not fragment:
            return None
        normalized = fragment.lstrip("#").strip()
        return normalized or None

    @staticmethod
    def _is_footer_row(
        cells: Sequence[Tag],
        cleaned_cells: Sequence[str],
        headers: Sequence[str],
    ) -> bool:
        if not cleaned_cells:
            return False
        if len(cleaned_cells) != 1:
            return False
        if not cleaned_cells[0].lower().startswith("source"):
            return False
        colspan = cells[0].get("colspan")
        if colspan is None:
            return True
        try:
            return int(colspan) >= len(headers)
        except ValueError:
            return True

    @staticmethod
    def _expand_row_cells(
        cells: Sequence[Tag],
        headers: Sequence[str],
        pending_rowspans: dict[int, dict[str, object]],
    ) -> list[Tag]:
        expanded: list[Tag] = []
        col_index = 0

        def consume_pending() -> None:
            nonlocal col_index
            while col_index < len(headers) and col_index in pending_rowspans:
                pending = pending_rowspans[col_index]
                cell = pending["cell"]
                remaining = int(pending["remaining"])
                expanded.append(cell)
                remaining -= 1
                if remaining <= 0:
                    pending_rowspans.pop(col_index, None)
                else:
                    pending_rowspans[col_index] = {
                        "cell": cell,
                        "remaining": remaining,
                    }
                col_index += 1

        for cell in cells:
            consume_pending()
            if col_index >= len(headers):
                break

            colspan = cell.get("colspan")
            rowspan = cell.get("rowspan")
            try:
                colspan_value = int(colspan) if colspan else 1
            except ValueError:
                colspan_value = 1
            try:
                rowspan_value = int(rowspan) if rowspan else 1
            except ValueError:
                rowspan_value = 1

            for offset in range(colspan_value):
                if col_index >= len(headers):
                    break
                expanded.append(cell)
                if rowspan_value > 1:
                    pending_rowspans[col_index] = {
                        "cell": cell,
                        "remaining": rowspan_value - 1,
                    }
                col_index += 1

        consume_pending()

        return expanded
