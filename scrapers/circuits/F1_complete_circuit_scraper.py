from __future__ import annotations

import time
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

from scrapers.base.F1_scraper import F1Scraper
from scrapers.base.F1_table_scraper import F1TableScraper
from scrapers.circuits.F1_circuits_list_scraper import F1CircuitsListScraper
from scrapers.helpers.f1_table_utils import clean_wiki_text, extract_links_from_cell
from scrapers.circuits.F1_circuit_infobox_scraper import F1CircuitInfoboxScraper


class _CircuitTableScraper(F1TableScraper):
    """Lekki scraper pojedynczej tabeli Wikipedii z zamianą linków na absolutne."""

    def __init__(
        self,
        *,
        table: Tag,
        base_url: str,
        index: int,
        session: Optional[requests.Session] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(include_urls=True, session=session, headers=headers)
        self._table = table
        self._base_url = base_url
        self._index = index

    def _full_url(self, href: str | None) -> Optional[str]:
        if not href:
            return None
        return urljoin(self._base_url, href)

    def _find_table(self, soup: BeautifulSoup) -> Tag:
        # Ignorujemy `soup` – wiemy już, którą tabelę parsować
        return self._table

    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        table = self._find_table(soup)
        header_row = table.find("tr")
        headers: List[str] = []
        if header_row:
            headers = [
                clean_wiki_text(c.get_text(" ", strip=True))
                for c in header_row.find_all(["th", "td"])
            ]

        rows: List[List[Dict[str, Any]]] = []
        for tr in table.find_all("tr")[1:]:
            cells = tr.find_all(["td", "th"])
            if not cells or all(not c.get_text(strip=True) for c in cells):
                continue

            # sprawdzamy, czy to nie jest "footer" powtarzający nagłówki
            cleaned_cells = [
                clean_wiki_text(c.get_text(" ", strip=True)) for c in cells
            ]
            if headers and len(cleaned_cells) == len(headers) and cleaned_cells == headers:
                continue

            row: List[Dict[str, Any]] = []
            for cell in cells:
                text = clean_wiki_text(cell.get_text(" ", strip=True))
                links = extract_links_from_cell(cell, full_url=self._full_url)
                row.append({"text": text, "links": links})
            rows.append(row)

        caption = table.find("caption")
        caption_text = clean_wiki_text(caption.get_text(" ", strip=True)) if caption else None

        return [
            {
                "index": self._index,
                "caption": caption_text,
                "headers": headers,
                "rows": rows,
            }
        ]


class F1SingleCircuitScraper(F1Scraper):
    """
    Scraper pojedynczego toru – pobiera infobox i wszystkie tabele z artykułu Wikipedii.

    Dodatkowe heurystyki:
    - jeżeli artykuł nie ma kategorii typu '... circuit / racetrack / speedway ...'
      → zwracamy None (nie zbieramy dodatkowych informacji),
    - jeżeli URL ma fragment (#Bugatti_Circuit) → szukamy infoboksa i tabel tylko
      wewnątrz tej sekcji.
    """

    def __init__(
        self,
        *,
        session: Optional[requests.Session] = None,
        delay_seconds: float = 1.0,
        timeout: int = 10,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(include_urls=True, session=session, headers=headers)
        self.delay_seconds = delay_seconds
        self.timeout = timeout
        self.url: str = ""
        self._original_url: Optional[str] = None

    def fetch(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Zwraca dict z kluczami:
        - url     – oryginalny URL (z ewentualnym fragmentem),
        - infobox – wynik F1CircuitInfoboxScraper.parse_from_soup,
        - tables  – lista zparsowanych wikitabel.

        Jeżeli artykuł nie wygląda na tor/tor wyścigowy (brak odpowiednich kategorii),
        zwraca None (nie dokładamy szczegółów).
        """
        self._original_url = url

        # rozbijamy ewentualny fragment po "#"
        base_url, fragment = (url.split("#", 1) + [None])[:2]
        self.url = base_url

        soup_full = BeautifulSoup(self._download(), "html.parser")

        # 1) filtr po kategoriach – jeżeli to nie wygląda na tor, nie scrapujemy dalej
        if not self._is_circuit_like_article(soup_full):
            return None

        # 2) jeśli mamy fragment, zawężamy się do danej sekcji
        working_soup = soup_full
        if fragment:
            section = self._extract_section_by_id(soup_full, fragment)
            if section is not None:
                working_soup = section

        parsed = self._parse_soup(working_soup)
        return parsed[0] if parsed else None

    def _download(self) -> str:
        if not self.url:
            raise ValueError("URL must be set before downloading")

        if self.delay_seconds:
            time.sleep(self.delay_seconds)

        response = self.session.get(self.url, timeout=self.timeout)
        response.raise_for_status()
        return response.text

    # ------------------------------
    # Heurystyki: kategorie + sekcje
    # ------------------------------

    def _is_circuit_like_article(self, soup: BeautifulSoup) -> bool:
        """Sprawdza, czy artykuł wygląda na tor/tor wyścigowy po kategoriach."""
        cat_div = soup.find("div", id="mw-normal-catlinks")
        if not cat_div:
            return False

        keywords = [
            "circuit",
            "race track",
            "racetrack",
            "speedway",
            "raceway",
            "motor racing",
            "motorsport venue",
        ]
        for a in cat_div.find_all("a"):
            text = a.get_text(strip=True).lower()
            if any(kw in text for kw in keywords):
                return True
        return False

    def _extract_section_by_id(self, soup: BeautifulSoup, fragment: str) -> Optional[BeautifulSoup]:
        """
        Zwraca pod-drzewo z daną sekcją (#id) lub None, jeśli nie znaleziono.

        W praktyce:
        - szukamy elementu z id=fragment,
        - bierzemy nadrzędny nagłówek (h1–h6),
        - zbieramy jego rodzeństwa aż do kolejnego nagłówka – to jest zawartość sekcji.
        """
        span = soup.find(id=fragment)
        if not span:
            return None

        header = span.find_parent(["h1", "h2", "h3", "h4", "h5", "h6"])
        if not header:
            return None

        # Tworzymy sztucznego "roota" z samą sekcją
        container = BeautifulSoup("<div></div>", "html.parser")
        root = container.div
        root.append(header)

        for sib in header.next_siblings:
            if isinstance(sib, Tag) and sib.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                break
            root.append(sib)

        return container

    # ------------------------------
    # Parsowanie treści
    # ------------------------------

    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        return [
            {
                "url": self._original_url or self.url,
                "infobox": self._scrape_infobox(soup),
                "tables": self._scrape_tables(soup, base_url=self.url),
            }
        ]

    def _scrape_infobox(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Parsuje infobox toru z przekazanego soup.

        Logika filtrowania po kategoriach i zawężania do sekcji (#fragment)
        jest załatwiona na poziomie F1SingleCircuitScraper.fetch,
        więc tutaj po prostu parsujemy przekazany fragment drzewa.
        """
        infobox_scraper = F1CircuitInfoboxScraper(timeout=self.timeout)
        return infobox_scraper.parse_from_soup(soup)

    def _scrape_tables(self, soup: BeautifulSoup, *, base_url: str) -> List[Dict[str, Any]]:
        pass
        # """
        # Zwraca wszystkie tabele 'wikitable' z artykułu (lub z danej sekcji, jeśli
        # `soup` został wcześniej zawężony do sekcji).
        # """
        # tables: List[Dict[str, Any]] = []
        #
        # for idx, table in enumerate(
        #     soup.find_all("table", class_=lambda c: c and "wikitable" in c.split())
        # ):
        #     table_scraper = _CircuitTableScraper(
        #         table=table,
        #         base_url=base_url,
        #         index=idx,
        #         session=self.session,
        #     )
        #     # _parse_soup oczekuje soup, ale i tak używa self._table
        #     tables.extend(table_scraper._parse_soup(table))
        #
        # return tables


class F1CompleteCircuitScraper(F1Scraper):
    """
    Pobiera listę torów, a następnie zaciąga szczegóły każdego toru (infobox + tabele).

    Dla torów, których artykuł nie ma "circuit/racetrack"-podobnych kategorii,
    pole `details` będzie miało wartość None.
    """

    url = F1CircuitsListScraper.url

    def __init__(
        self,
        *,
        delay_seconds: float = 1.0,
        session: Optional[requests.Session] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(include_urls=True, session=session, headers=headers)
        self.delay_seconds = delay_seconds
        self.list_scraper = F1CircuitsListScraper(
            include_urls=True, session=self.session,
        )
        self.single_scraper = F1SingleCircuitScraper(
            session=self.session,
            delay_seconds=delay_seconds,
        )

    def fetch(self) -> List[Dict[str, Any]]:
        circuits = self.list_scraper.fetch()
        complete: List[Dict[str, Any]] = []

        for circuit in circuits:
            circuit_url: Optional[str] = None
            circuit_data = circuit.get("circuit")
            if isinstance(circuit_data, dict):
                circuit_url = circuit_data.get("url")

            details: Optional[Dict[str, Any]] = None
            if circuit_url:
                details = self.single_scraper.fetch(circuit_url)

            full_record = dict(circuit)
            full_record["details"] = details
            complete.append(full_record)

        self._data = complete
        return self._data

    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Metoda wymagana przez bazę – nie używana w tym scraperze."""
        raise NotImplementedError("Use fetch() bezpośrednio dla pełnego scrapingu")


if __name__ == "__main__":
    scraper = F1CompleteCircuitScraper(delay_seconds=1.0)
    data = scraper.fetch()
    print(f"Pobrano {len(data)} rekordów z pełnymi danymi torów.")

    scraper.to_json("../../data/wiki/circuits/f1_circuits_extended.json")
    scraper.to_csv("../../data/wiki/circuits/f1_circuits_extended.csv")
