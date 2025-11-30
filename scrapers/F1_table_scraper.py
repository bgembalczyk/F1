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
    - column_types    – typ danych dla danego KLUCZA (po column_map):
                         "auto" (domyślnie),
                         "text",
                         "list",
                         "seasons",
                         "skip",
                         "list_of_links",  # zawsze lista obiektów linków {text, url}
                         "link",           # NEW: pojedynczy link {text, url} lub None
    """

    _SKIP = object()

    section_id: Optional[str] = None
    expected_headers: Sequence[str] | None = None
    column_map: Mapping[str, str] = {}

    # konfiguracja typów kolumn po stronie scraperów potomnych:
    # np. {"years_held": "seasons", "country": "list", "grands_prix": "list_of_links"}
    column_types: Mapping[str, str] = {}

    table_css_class: str = "wikitable"

    # regex do przypisów Wikipedii: [1], [b], [note 3], [citation needed], ...
    _REF_RE = re.compile(r"\[\s*[^]]+\s*]")

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

    # --- pomocnicze ---

    def _clean_text(self, text: str) -> str:
        """
        Normalizacja whitespace + usunięcie przypisów Wikipedii.
        """
        t = text.replace("\xa0", " ").replace("&nbsp;", " ")
        t = self._REF_RE.sub("", t)
        return t.strip()

    def _value_to_text(self, value: Any) -> Optional[str]:
        """
        Używane przy column_types[key] == "text".
        Zamienia dict/list na tekst.
        """
        if value is None:
            return None
        if isinstance(value, dict):
            return value.get("text") or ""
        if isinstance(value, list):
            parts: List[str] = []
            for item in value:
                parts.append(self._value_to_text(item) or "")
            return ", ".join(p for p in parts if p)
        return str(value)

    def _parse_seasons(self, text: str) -> list[dict[str, Any]]:
        """
        Zamienia tekst w stylu '1973, 1975–1982, 1984' na listę:
        [{"year": 1973, "url": ...}, {"year": 1975, "url": ...}, ..., {"year": 1984, "url": ...}]
        """
        result: list[dict[str, Any]] = []
        seen: set[int] = set()

        if not text:
            return result

        parts = [p.strip() for p in text.split(",") if p.strip()]

        for part in parts:
            # zakres: 1975–1982 (en dash lub zwykły minus)
            m_range = re.fullmatch(r"(\d{4})\s*[\u2013-]\s*(\d{4})", part)
            if m_range:
                start = int(m_range.group(1))
                end = int(m_range.group(2))
                if end < start:
                    start, end = end, start  # na wszelki wypadek
                years = range(start, end + 1)
            else:
                # pojedynczy rok: 1973
                m_year = re.fullmatch(r"\d{4}", part)
                if not m_year:
                    continue
                years = [int(part)]

            for y in years:
                if y in seen:
                    continue
                seen.add(y)
                url = f"https://en.wikipedia.org/wiki/{y}_Formula_One_World_Championship"
                result.append({"year": y, "url": url})

        return result

    # NEW: helper do wyciągania listy linków z komórki
    def _extract_links_from_cell(self, cell: Tag) -> list[dict[str, Any]]:
        """
        Zwraca listę linków {text, url} z komórki,
        ignorując linki będące przypisami (cite_note/reference).
        """
        links: list[dict[str, Any]] = []

        for a in cell.find_all("a", href=True):
            href = a.get("href") or ""
            classes = a.get("class") or []

            # 1) Ignore typical reference / footnote links
            #    <a href="#cite_note-..." class="reference">[14]</a>
            if "cite_note" in href:
                continue
            if any(cls in ("reference", "mw-cite-backlink") for cls in classes):
                continue

            text = self._clean_text(a.get_text(" ", strip=True))

            # 2) Dodatkowy bezpiecznik – jak tekst jest pusty i to lokalny anchor,
            #    to też traktujemy jako przypis / techniczny link.
            if not text and href.startswith("#"):
                continue

            url = self._full_url(href)
            links.append({"text": text, "url": url})

        return links

    def _apply_column_type(
        self,
        header: str,
        key: str,
        value: Any,
        clean_text: str,
        col_type: Optional[str] = None,
    ) -> Any:
        """
        Typy:
        - "skip"    -> kolumna ignorowana
        - "seasons" -> specjalny parser sezonów (lista dictów {year,url})
        - "text"    -> zawsze string
        - "list"    -> zawsze lista
        - "list_of_links" -> zawsze lista dictów {text, url}
        - "link"    -> pojedynczy dict {text, url} lub None
        - brak/auto -> bez zmian
        """
        if col_type is None:
            col_type = self.column_types.get(header) or self.column_types.get(key) or "auto"

        if col_type == "skip":
            return self._SKIP

        if col_type == "seasons":
            return self._parse_seasons(clean_text)

        if col_type == "text":
            if isinstance(value, dict):
                return value.get("text")
            if isinstance(value, list):
                parts: list[str] = []
                for item in value:
                    if isinstance(item, dict):
                        parts.append(str(item.get("text", "")))
                    else:
                        parts.append(str(item))
                return ", ".join(p for p in parts if p)
            return value

        if col_type == "list":
            if value is None:
                return []
            if isinstance(value, list):
                return value
            return [value]

        if col_type == "link":
            # normalizujemy do pojedynczego dicta lub None
            if isinstance(value, list):
                return value[0] if value else None
            if isinstance(value, dict):
                return value
            if value is None:
                return None
            # jeżeli coś innego (np. sam tekst) – zrób z tego link bez URL
            return {"text": str(value), "url": None}

        if col_type == "list_of_links":
            if value is None:
                return []
            if isinstance(value, list):
                return value
            return [value]

        # auto
        return value

    # --- hook per-wiersz ---

    def parse_row(
        self,
        row: Tag,
        cells: Sequence[Tag],
        headers: Sequence[str],
    ) -> Optional[Dict[str, Any]]:
        """
        Zasady:
        - normalizujemy whitespace (&nbsp;, \xa0),
        - usuwamy przypisy Wikipedii w [],
        - auto-linkowanie:
          * 1 link → dict{text, url}
          * tylko linki+przecinki → lista dictów
          * inaczej → tekst,
        - kolumny typu "list_of_links" → zawsze lista linków {text, url} z <a>,
        - kolumny typu "link"         → pojedynczy link {text, url} (lub None),
        - na końcu stosujemy column_types (skip / seasons / text / list / list_of_links / link / auto).
        """
        record: Dict[str, Any] = {}

        for header, cell in zip(headers, cells):
            key = self.column_map.get(header, self._normalize_header(header))

            raw_text = cell.get_text(" ", strip=True)
            clean_text = self._clean_text(raw_text)

            # typ kolumny
            col_type = self.column_types.get(header) or self.column_types.get(key) or "auto"

            if col_type == "list_of_links":
                # zawsze lista linków z filtra referencji
                value: Any = self._extract_links_from_cell(cell)

            elif col_type == "link":
                # pojedynczy link – bierzemy pierwszy sensowny z komórki
                links = self._extract_links_from_cell(cell)
                if not links:
                    value = None
                else:
                    value = links[0]

            else:
                value = clean_text  # domyślnie tekst

                if self.include_urls:
                    links = [a for a in cell.find_all("a", href=True)]

                    # 1) Jeden link → dict{text, url}
                    if len(links) == 1:
                        a = links[0]
                        href = a.get("href")
                        url = self._full_url(href)
                        if url:
                            value = {
                                "text": clean_text,
                                "url": url,
                            }

                    # 2) Wiele linków → tylko linki+przecinki → lista dictów
                    elif len(links) > 1:
                        raw_html = "".join(str(x) for x in cell.contents)
                        cleaned_html = re.sub(r"\s+|&nbsp;|\xa0", "", raw_html)
                        tmp = cleaned_html

                        for a in links:
                            link_html = re.sub(r"\s+|&nbsp;|\xa0", "", str(a))
                            tmp = tmp.replace(link_html, "")

                        if all(ch == "," for ch in tmp if ch != ""):
                            list_value: list[dict[str, Any]] = []
                            for a in links:
                                t = a.get_text(" ", strip=True)
                                t = self._clean_text(t)
                                href = a.get("href")
                                url = self._full_url(href)
                                list_value.append({"text": t, "url": url})
                            value = list_value

            # zastosuj typ kolumny (drugi etap)
            value = self._apply_column_type(header, key, value, clean_text, col_type=col_type)

            if value is self._SKIP:
                continue

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
