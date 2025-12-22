from __future__ import annotations

import logging
from typing import Optional, Sequence

from bs4 import BeautifulSoup, Tag

from scrapers.base.helpers.html_utils import find_section_elements
from scrapers.base.helpers.tables import is_repeated_header_row
from scrapers.base.helpers.text_normalization import clean_wiki_text
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
            if self._is_repeated_header_row(cleaned_cells, headers):
                logger.debug("Pomijam powtórzony wiersz nagłówka w tabeli.")
                continue

            if cells:
                records.append(TableRow(headers=headers, cells=cells, raw_tr=tr))

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

        header_set = set(headers)
        return all(h in header_set for h in self.expected_headers)

    @staticmethod
    def _normalize_fragment(fragment: Optional[str]) -> Optional[str]:
        if not fragment:
            return None
        normalized = fragment.lstrip("#").strip()
        return normalized or None

    @staticmethod
    def _is_repeated_header_row(
        cleaned_cells: Sequence[str],
        headers: Sequence[str],
    ) -> bool:
        return is_repeated_header_row(cleaned_cells, headers)
