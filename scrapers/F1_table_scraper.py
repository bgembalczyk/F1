from __future__ import annotations

import re
from abc import ABC
from typing import Optional, Sequence, Mapping, List, Dict, Any, Iterable

from bs4 import BeautifulSoup, Tag

from scrapers.F1_scraper import F1Scraper


class F1TableScraper(F1Scraper, ABC):
    """
    Scraper oparty o pojedynczą tabelę 'wikitable'.

    Konfiguracja przez pola klasowe:

    - section_id      – id nagłówka sekcji (np. "Constructors_for_the_2025_season"),
                         jeśli None – szukamy po całej stronie.
    - expected_headers – lista nagłówków, które MUSZĄ wystąpić w tabeli (podzbiór).
    - column_map      – mapowanie "nagłówek z tabeli" -> "klucz w dict".
    - url_columns     – opcjonalnie: nagłówki, dla których NAWET przy wielu linkach
                         w komórce chcemy specjalnie obsłużyć URL-e
                         (konkretne użycie zostawiamy klasom potomnym / override).
    """

    section_id: Optional[str] = None
    expected_headers: Sequence[str] | None = None
    column_map: Mapping[str, str] = {}
    url_columns: Sequence[str] = ()

    table_css_class: str = "wikitable"

    # --- szablon parsowania ---

    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        table = self._find_table(soup)
        header_row = table.find("tr")
        if not header_row:
            raise RuntimeError("Nie znaleziono wiersza nagłówkowego w tabeli.")

        header_cells = header_row.find_all(["th", "td"])
        headers = [c.get_text(" ", strip=True) for c in header_cells]

        records: List[Dict[str, Any]] = []
        for tr in table.find_all("tr")[1:]:
            cells = tr.find_all(["td", "th"])
            # omijamy np. puste wiersze / separatory
            if not cells or all(not c.get_text(strip=True) for c in cells):
                continue

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
            headers = [c.get_text(" ", strip=True) for c in header_cells]

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
        Zasady:
        - zawsze normalizujemy whitespace (zwł. &nbsp;, \xa0)
        - jeśli komórka zawiera tylko jeden link → dict(text, url)
        - jeśli komórka zawiera wyłącznie linki + przecinki → lista dictów
        - w przeciwnym razie → zwykły string
        """
        record: Dict[str, Any] = {}

        for header, cell in zip(headers, cells):
            key = self.column_map.get(header, self._normalize_header(header))

            # --- normalizacja whitespace ---
            raw_text = cell.get_text(" ", strip=True)
            clean_text = (
                raw_text.replace("\xa0", " ")
                .replace("&nbsp;", " ")
            )

            value: Any = clean_text  # domyślnie zwykły tekst

            if self.include_urls:
                links = [a for a in cell.find_all("a", href=True)]

                # --- 1) Jeden link → dict ---
                if len(links) == 1:
                    a = links[0]
                    href = a.get("href")
                    url = self._full_url(href)
                    if url:
                        value = {
                            "text": clean_text,
                            "url": url,
                        }

                # --- 2) Wiele linków → sprawdź, czy komórka to tylko linki + przecinki ---
                elif len(links) > 1:
                    import re

                    # surowe HTML wewnątrz komórki
                    raw_html = "".join(str(x) for x in cell.contents)

                    # całkowita normalizacja whitespace → usuń wszelki \s, w tym NBSP
                    cleaned_html = re.sub(r"\s+|&nbsp;|\xa0", "", raw_html)

                    tmp = cleaned_html

                    # usuń wszystkie <a>…</a>
                    for a in links:
                        link_html = re.sub(r"\s+|&nbsp;|\xa0", "", str(a))
                        tmp = tmp.replace(link_html, "")

                    # jeśli zostały tylko przecinki → lista linków
                    if all(ch == "," for ch in tmp if ch != ""):
                        value = []
                        for a in links:
                            t = a.get_text(" ", strip=True)
                            t = t.replace("\xa0", " ").replace("&nbsp;", " ")
                            href = a.get("href")
                            url = self._full_url(href)
                            value.append({
                                "text": t,
                                "url": url,
                            })

            record[key] = value

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
