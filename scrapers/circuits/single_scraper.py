import time
from typing import Optional, Dict, Any, List

import requests
from bs4 import BeautifulSoup, Tag

from scrapers.base.infobox.circuits.scraper import F1CircuitInfoboxScraper
from scrapers.base.mixins.wiki_sections import WikipediaSectionByIdMixin
from scrapers.base.scraper import F1Scraper


class F1SingleCircuitScraper(WikipediaSectionByIdMixin, F1Scraper):
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
        include_urls: bool = True,
        session: Optional[requests.Session] = None,
        delay_seconds: float = 1.0,
        timeout: int = 10,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(include_urls=include_urls, session=session, headers=headers)
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
        ]
        for a in cat_div.find_all("a"):
            text = a.get_text(strip=True).lower()
            if any(kw in text for kw in keywords):
                return True
        return False

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

    def _scrape_tables(
        self, soup: BeautifulSoup, *, base_url: str
    ) -> List[Dict[str, Any]]:
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
