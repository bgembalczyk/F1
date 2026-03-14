import logging
from collections.abc import Sequence

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.base.helpers.html_utils import find_section_elements
from scrapers.base.helpers.tables.header import is_repeated_header_row
from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.table.headers import normalize_header
from scrapers.base.table.row import TableRow

logger = logging.getLogger(__name__)

HEADER_ROWS_WITH_SUBHEADERS = 2


class HtmlTableParser:
    """
    Parser tabel HTML, który zwraca listę wierszy jako mapowania
    nagłówków na komórki.
    """

    def __init__(
        self,
        *,
        section_id: str | None = None,
        fragment: str | None = None,
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
        return self.parse_table(table)

    def parse_table(self, table: Tag) -> list[TableRow]:
        headers, header_cells, header_rows = self._extract_headers(table)

        records: list[TableRow] = []
        pending_rowspans: dict[int, dict[str, object]] = {}
        for tr in table.find_all("tr")[header_rows:]:
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

            expanded_cells = self._expand_row_cells(
                cells,
                headers,
                pending_rowspans,
            )
            records.append(
                TableRow(
                    headers=headers,
                    cells=expanded_cells,
                    raw_tr=tr,
                    header_cells=header_cells,
                ),
            )

        return records

    def _find_table(self, soup: BeautifulSoup) -> Tag:
        section_id = self.section_id or self._normalize_fragment(self.fragment)
        candidate_tables = find_section_elements(
            soup,
            section_id,
            ["table"],
            class_=self.table_css_class,
        )

        for table in candidate_tables:
            try:
                headers, _, _ = self._extract_headers(table)
            except RuntimeError:
                continue

            if self._headers_match(headers):
                return table

        msg = "Nie znaleziono pasującej tabeli."
        raise RuntimeError(msg)

    def _headers_match(self, headers: Sequence[str]) -> bool:
        if not self.expected_headers:
            return True

        header_set = {normalize_header(h) for h in headers}
        expected = {normalize_header(h) for h in self.expected_headers}
        return all(h in header_set for h in expected)

    @staticmethod
    def _normalize_fragment(fragment: str | None) -> str | None:
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

        for cell in cells:
            col_index = HtmlTableParser._consume_pending(
                expanded,
                col_index,
                headers,
                pending_rowspans,
            )
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

            for _offset in range(colspan_value):
                if col_index >= len(headers):
                    break
                expanded.append(cell)
                if rowspan_value > 1:
                    pending_rowspans[col_index] = {
                        "cell": cell,
                        "remaining": rowspan_value - 1,
                    }
                col_index += 1

        HtmlTableParser._consume_pending(expanded, col_index, headers, pending_rowspans)

        return expanded

    @staticmethod
    def _consume_pending(
        expanded: list[Tag],
        col_index: int,
        headers: Sequence[str],
        pending_rowspans: dict[int, dict[str, object]],
    ) -> int:
        """Konsumuje oczekujące rowspany dla kolumny.

        Zwraca zaktualizowany ``col_index``.
        """
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
        return col_index

    def _clean_cells(self, cells: Sequence[Tag]) -> list[str]:
        return [
            clean_wiki_text(
                c.get_text(" ", strip=True),
                strip_lang_suffix=self.strip_lang_suffix,
                strip_refs=self.strip_refs,
                normalize_dashes=self.normalize_dashes,
            )
            for c in cells
        ]

    @staticmethod
    def _has_multirow_header(
        first_cells: Sequence[Tag],
        second_cells: Sequence[Tag],
    ) -> bool:
        return (
            bool(second_cells)
            and all(cell.name == "th" for cell in second_cells)
            and any(int(cell.get("colspan") or 1) > 1 for cell in first_cells)
        )

    @staticmethod
    def _combine_header_rows(
        first_cells: Sequence[Tag],
        first_headers: Sequence[str],
        second_cells: Sequence[Tag],
        second_headers: Sequence[str],
    ) -> tuple[list[str], list[Tag]]:
        combined: list[str] = []
        combined_cells: list[Tag] = []
        second_index = 0
        for cell, header in zip(first_cells, first_headers, strict=False):
            try:
                colspan_value = int(cell.get("colspan") or 1)
            except ValueError:
                colspan_value = 1
            try:
                rowspan_value = int(cell.get("rowspan") or 1)
            except ValueError:
                rowspan_value = 1

            if rowspan_value > 1 or colspan_value == 1:
                combined.extend([header] * colspan_value)
                combined_cells.extend([cell] * colspan_value)
                continue

            for _ in range(colspan_value):
                if second_index < len(second_headers):
                    combined.append(second_headers[second_index])
                    combined_cells.append(second_cells[second_index])
                else:
                    combined.append(header)
                    combined_cells.append(cell)
                second_index += 1

        return combined, combined_cells

    def _extract_headers(self, table: Tag) -> tuple[list[str], list[Tag], int]:
        rows = table.find_all("tr")
        if not rows:
            msg = "Nie znaleziono wiersza nagłówkowego w tabeli."
            raise RuntimeError(msg)

        first_row = rows[0]
        first_cells = first_row.find_all(["th", "td"])
        if not first_cells:
            msg = "Nie znaleziono wiersza nagłówkowego w tabeli."
            raise RuntimeError(msg)

        first_headers = self._clean_cells(first_cells)

        if len(rows) < HEADER_ROWS_WITH_SUBHEADERS:
            return first_headers, first_cells, 1

        second_row = rows[1]
        second_cells = second_row.find_all(["th", "td"])
        if not self._has_multirow_header(first_cells, second_cells):
            return first_headers, first_cells, 1

        second_headers = self._clean_cells(second_cells)
        combined, combined_cells = self._combine_header_rows(
            first_cells,
            first_headers,
            second_cells,
            second_headers,
        )
        return combined, combined_cells, HEADER_ROWS_WITH_SUBHEADERS
