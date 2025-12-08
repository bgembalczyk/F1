from __future__ import annotations

from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup, Tag

from f1_http.interfaces import HttpClientProtocol
from http_client import HttpClient
from scrapers.base.infobox.mixins.circuits.entities import CircuitEntitiesMixin
from scrapers.base.infobox.mixins.circuits.layouts import CircuitInfoboxLayoutsMixin
from scrapers.base.infobox.scraper import WikipediaInfoboxScraper
from scrapers.base.mixins.wiki_sections import WikipediaSectionByIdMixin
from scrapers.base.scraper import F1Scraper


class F1CircuitInfoboxScraper(
    WikipediaSectionByIdMixin,
    CircuitEntitiesMixin,
    CircuitInfoboxLayoutsMixin,
    F1Scraper,
    WikipediaInfoboxScraper,
):
    """Parser infoboksów torów F1 z heurystykami pod typowe pola."""

    def __init__(
        self,
        *,
        timeout: int = 10,
        include_urls: bool = True,
        session: Optional[requests.Session] = None,
        headers: Optional[Dict[str, str]] = None,
        http_client: Optional[HttpClientProtocol] = None,
    ) -> None:
        F1Scraper.__init__(
            self,
            include_urls=include_urls,
            session=session,
            headers=headers,
            http_client=http_client,
            timeout=timeout,
        )
        WikipediaInfoboxScraper.__init__(
            self,
            timeout=timeout,
            session=self.session,
            headers=headers,
            http_client=self.http_client,
        )
        self.url: str = ""

    # ------------------------------
    # Publiczne API
    # ------------------------------

    def fetch(self, url: str) -> Dict[str, Any]:
        """
        Główne API używane wewnętrznie – obsługuje #fragment (sekcje),
        przycina infoboksy po infobox-full-data itd.
        """
        self.url = url
        base_url, fragment = (url.split("#", 1) + [None])[:2]
        self.url = base_url

        html = self._download()
        full_soup = BeautifulSoup(html, "html.parser")

        if not self._is_circuit_like_article(full_soup):
            title = full_soup.title.get_text(strip=True) if full_soup.title else None
            return self._prune_nulls(
                {
                    "url": url,
                    "title": title,
                },
            )

        soup = full_soup
        if fragment:
            section = self._extract_section_by_id(full_soup, fragment)
            if section is not None:
                soup = section

        return self.parse_from_soup(soup)

    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """API bazowej klasy – deleguje do parse_from_soup."""
        return [self.parse_from_soup(soup)]

    # >>> ZMIANA TUTAJ <<<
    def parse_from_soup(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Zwraca znormalizowany infobox + layouts (bez surowego `rows`).

        Od pierwszego wiersza z class="infobox-full-data" w danej tabeli
        infoboksa ignorujemy resztę wierszy (wycinamy je z DOM-u),
        żeby nie mieszać danych z pełnotabelarycznymi statystykami.
        """
        truncated_soup = self._truncate_infobox_after_full_data(soup)

        # parsujemy infobox już bez "ogonów" po infobox-full-data
        raw = super().parse_from_soup(truncated_soup)

        # layouty wciąż parsujemy z pełnej sekcji artykułu
        layout_records = self._parse_layout_sections(soup)
        return self._with_normalized(raw, layout_records)

    # ------------------------------
    # Helper: przycinanie infoboksa
    # ------------------------------

    def _truncate_infobox_after_full_data(self, soup: BeautifulSoup) -> BeautifulSoup:
        """
        W każdej tabeli infoboksa usuwamy:
        - pierwszy wiersz, który ma klasę `infobox-full-data`
          LUB zawiera komórkę (td/th) z tą klasą,
        - wszystkie kolejne wiersze poniżej.
        """

        # helper: tabela ma mieć klasę zawierającą 'infobox'
        def _has_infobox_class(classes: Any) -> bool:
            if not classes:
                return False
            if isinstance(classes, str):
                classes = classes.split()
            return "infobox" in classes

        # każda tabela infoboksa
        for table in soup.find_all("table", class_=_has_infobox_class):
            rows: List[Tag] = table.find_all("tr")

            cut_index: Optional[int] = None
            for idx, row in enumerate(rows):
                row_classes = row.get("class") or []
                if isinstance(row_classes, str):
                    row_classes = row_classes.split()

                has_full_on_tr = "infobox-full-data" in row_classes
                has_full_in_cell = row.find(["td", "th"], class_="infobox-full-data") is not None

                if has_full_on_tr or has_full_in_cell:
                    cut_index = idx
                    break

            # jeśli znaleziono początek sekcji 'full-data' → usuń wszystko od tego miejsca
            if cut_index is not None:
                for r in rows[cut_index:]:
                    r.decompose()

        return soup

    # ------------------------------
    # Pobieranie / sekcje / kategorie
    # ------------------------------

    def _download(self) -> str:
        if not self.url:
            raise ValueError("URL must be set before downloading")
        return self.http_client.get_text(self.url, timeout=self.timeout)

    def _is_circuit_like_article(self, soup: BeautifulSoup) -> bool:
        """Sprawdza czy artykuł wygląda na tor/tor wyścigowy po kategoriach."""
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
