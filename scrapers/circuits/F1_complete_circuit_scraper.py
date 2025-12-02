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
        self.url = ""

    def fetch(self, url: str) -> Dict[str, Any]:
        self.url = url
        soup = BeautifulSoup(self._download(), "html.parser")
        parsed = self._parse_soup(soup)
        return parsed[0] if parsed else {}

    def _download(self) -> str:
        if not self.url:
            raise ValueError("URL must be set before downloading")

        if self.delay_seconds:
            time.sleep(self.delay_seconds)

        response = self.session.get(self.url, timeout=self.timeout)
        response.raise_for_status()
        return response.text

    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        return [
            {
                "url": self.url,
                "infobox": self._scrape_infobox(soup),
                "tables": self._scrape_tables(soup, base_url=self.url),
            }
        ]

    def _scrape_infobox(self, soup: BeautifulSoup) -> Dict[str, Any]:
        infobox_scraper = F1CircuitInfoboxScraper(timeout=self.timeout)
        return infobox_scraper.parse_from_soup(soup)

    def _scrape_tables(self, soup: BeautifulSoup, *, base_url: str) -> List[Dict[str, Any]]:
        tables: List[Dict[str, Any]] = []

        for idx, table in enumerate(
            soup.find_all(
                "table", class_=lambda c: c and "wikitable" in c.split()
            )
        ):
            table_scraper = _CircuitTableScraper(
                table=table, base_url=base_url, index=idx, session=self.session
            )
            tables.extend(table_scraper._parse_soup(table))

        return tables


class F1CompleteCircuitScraper(F1Scraper):
    """
    Pobiera listę torów, a następnie zaciąga szczegóły każdego toru (infobox + tabele).
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
            include_urls=True, session=self.session
        )
        self.single_scraper = F1SingleCircuitScraper(
            session=self.session, delay_seconds=delay_seconds
        )

    def fetch(self) -> List[Dict[str, Any]]:
        circuits = self.list_scraper.fetch()
        complete: List[Dict[str, Any]] = []

        for circuit in circuits:
            circuit_url = None
            circuit_data = circuit.get("circuit")
            if isinstance(circuit_data, dict):
                circuit_url = circuit_data.get("url")

            details = None
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
