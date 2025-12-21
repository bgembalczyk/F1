from __future__ import annotations

import re
from typing import Optional, Sequence

from bs4 import BeautifulSoup, Tag

from scrapers.base.helpers.wiki import find_section_elements, clean_wiki_text


class HtmlTableParser:
    """
    Parser tabel HTML, który zwraca listę wierszy jako mapowania
    nagłówków na komórki.
    """

    _REF_RE = re.compile(r"\[\s*[^]]+\s*]")

    def __init__(
        self,
        *,
        section_id: Optional[str] = None,
        expected_headers: Sequence[str] | None = None,
        table_css_class: str = "wikitable",
    ) -> None:
        self.section_id = section_id
        self.expected_headers = expected_headers
        self.table_css_class = table_css_class

    def parse(self, soup: BeautifulSoup) -> list[dict[str, Tag]]:
        table = self._find_table(soup)
        header_row = table.find("tr")
        if not header_row:
            raise RuntimeError("Nie znaleziono wiersza nagłówkowego w tabeli.")

        header_cells = header_row.find_all(["th", "td"])
        headers = [clean_wiki_text(c.get_text(" ", strip=True)) for c in header_cells]

        records: list[dict[str, Tag]] = []
        for tr in table.find_all("tr")[1:]:
            cells = tr.find_all(["td", "th"])

            if not cells or all(not c.get_text(strip=True) for c in cells):
                continue

            cleaned_cells = [
                clean_wiki_text(c.get_text(" ", strip=True)) for c in cells
            ]
            if self._is_repeated_header_row(cleaned_cells, headers):
                continue

            row = dict(zip(headers, cells))
            if row:
                records.append(row)

        return records

    def _find_table(self, soup: BeautifulSoup) -> Tag:
        candidate_tables = find_section_elements(
            soup, self.section_id, ["table"], class_=self.table_css_class
        )

        for table in candidate_tables:
            header_row = table.find("tr")
            if not header_row:
                continue
            header_cells = header_row.find_all(["th", "td"])
            headers = [
                clean_wiki_text(c.get_text(" ", strip=True)) for c in header_cells
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
    def _is_repeated_header_row(
        cleaned_cells: Sequence[str],
        headers: Sequence[str],
    ) -> bool:
        return len(cleaned_cells) == len(headers) and list(cleaned_cells) == list(
            headers
        )
