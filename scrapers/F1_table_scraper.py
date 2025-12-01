from __future__ import annotations

import re
from abc import ABC
from typing import Optional, Sequence, Mapping, List, Dict, Any, Iterable

from bs4 import BeautifulSoup, Tag

from scrapers.F1_scraper import F1Scraper
from scrapers.helpers.columns.column_context import ColumnContext
from scrapers.helpers.columns.columns import BaseColumn, AutoColumn
from scrapers.helpers.f1_table_utils import clean_wiki_text, extract_links_from_cell


class F1TableScraper(F1Scraper, ABC):
    """
    Scraper oparty o pojedynczą tabelę 'wikitable'.

    Konfiguracja przez pola klasowe:

    - section_id    – id nagłówka sekcji (np. "Constructors_for_the_2025_season"),
                       jeśli None – szukamy po całej stronie.
    - expected_headers – lista nagłówków, które MUSZĄ wystąpić w tabeli (podzbiór).
    - column_map    – mapowanie "nagłówek z tabeli" -> "klucz w dict".
    - columns       – mapowanie klucza/nagłówka -> BaseColumn
                      (MultiColumn / FuncColumn / TextColumn / IntColumn / ...).
    """

    _SKIP = object()

    section_id: Optional[str] = None
    expected_headers: Sequence[str] | None = None
    column_map: Mapping[str, str] = {}

    # klucz (po column_map) lub nagłówek -> BaseColumn
    columns: Mapping[str, BaseColumn] = {}

    table_css_class: str = "wikitable"

    _REF_RE = re.compile(r"\[\s*[^]]+\s*]")

    # domyślna kolumna dla pól, które nie mają przypisanej logiki
    default_column: BaseColumn = AutoColumn()

    # --- szablon parsowania ---

    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        table = self._find_table(soup)
        header_row = table.find("tr")
        if not header_row:
            raise RuntimeError("Nie znaleziono wiersza nagłówkowego w tabeli.")

        header_cells = header_row.find_all(["th", "td"])
        headers = [
            clean_wiki_text(c.get_text(" ", strip=True))
            for c in header_cells
        ]

        records: List[Dict[str, Any]] = []
        for tr in table.find_all("tr")[1:]:
            cells = tr.find_all(["td", "th"])

            # omijamy np. puste wiersze / separatory
            if not cells or all(not c.get_text(strip=True) for c in cells):
                continue

            # --- nowy fragment: pomijamy footer/powtórzony nagłówek ---
            cleaned_cells = [
                clean_wiki_text(c.get_text(" ", strip=True))
                for c in cells
            ]
            if len(cleaned_cells) == len(headers) and cleaned_cells == list(headers):
                # wiersz, który ma dokładnie to samo co nagłówki -> traktujemy jako footer
                continue
            # --- koniec nowego fragmentu ---

            record = self.parse_row(tr, cells, headers)
            if record:
                records.append(record)

        return records

    # --- szukanie odpowiedniej tabeli ---

    def _find_table(self, soup: BeautifulSoup) -> Tag:
        """
        Znajduje tabelę na podstawie section_id i / lub expected_headers.
        """
        candidate_tables: Iterable[Tag]

        if self.section_id:
            # Szukamy nagłówka z danym id i pierwszej tabeli po nim
            heading = soup.find(id=self.section_id)
            if not heading:
                raise RuntimeError(f"Nie znaleziono sekcji o id={self.section_id!r}")
            candidate_tables = heading.find_all_next(
                "table", class_=self.table_css_class
            )
        else:
            candidate_tables = soup.find_all("table", class_=self.table_css_class)

        for table in candidate_tables:
            header_row = table.find("tr")
            if not header_row:
                continue
            header_cells = header_row.find_all(["th", "td"])
            headers = [
                clean_wiki_text(c.get_text(" ", strip=True))
                for c in header_cells
            ]

            if self._headers_match(headers):
                return table

        raise RuntimeError("Nie znaleziono pasującej tabeli.")

    def _headers_match(self, headers: Sequence[str]) -> bool:
        """
        Domyślnie: jeśli expected_headers jest ustawione, to sprawdzamy,
        czy wszystkie jej elementy występują w 'headers' (kolejność nieistotna).
        Jeśli expected_headers = None -> bierzemy pierwszą napotkaną tabelę.
        """
        if not self.expected_headers:
            return True

        header_set = set(headers)
        return all(h in header_set for h in self.expected_headers)

    # --- hook per-wiersz ---

    def parse_row(
        self,
        row: Tag,
        cells: Sequence[Tag],
        headers: Sequence[str],
    ) -> Optional[Dict[str, Any]]:
        """
        Dla każdej komórki:
        - ustala nagłówek i klucz,
        - wybiera typ kolumny z column_types,
        - deleguje całą logikę do handlera kolumny.
        """
        record: Dict[str, Any] = {}

        for header, cell in zip(headers, cells):
            key = self.column_map.get(header, self._normalize_header(header))

            raw_text = cell.get_text(" ", strip=True)
            clean_text = clean_wiki_text(raw_text)

            links: list[dict[str, Any]] = []
            if self.include_urls:
                links = extract_links_from_cell(cell, full_url=self._full_url)

            ctx = ColumnContext(
                header=header,
                key=key,
                raw_text=raw_text,
                clean_text=clean_text,
                links=links,
                cell=cell,
                skip_sentinel=self._SKIP,
            )

            col = (
                self.columns.get(key)
                or self.columns.get(header)
                or self.default_column
            )

            col.apply(ctx, record)

        return record

    @staticmethod
    def _normalize_header(header: str) -> str:
        return (
            header.strip()
            .lower()
            .replace(" ", "_")
            .replace("(", "")
            .replace(")", "")
            .replace("/", "_")
        )
