from __future__ import annotations

from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup, Tag

from scrapers.base.infobox.mixins.circuits.entities import CircuitEntitiesMixin
from scrapers.base.infobox.mixins.circuits.layouts import CircuitInfoboxLayoutsMixin
from scrapers.base.infobox.scraper import WikipediaInfoboxScraper
from scrapers.base.scraper import F1Scraper


class F1CircuitInfoboxScraper(
    CircuitEntitiesMixin, CircuitInfoboxLayoutsMixin, F1Scraper, WikipediaInfoboxScraper
):
    """Parser infoboksów torów F1 z heurystykami pod typowe pola."""

    def __init__(
        self,
        *,
        timeout: int = 10,
        include_urls: bool = True,
        session: Optional[requests.Session] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        F1Scraper.__init__(
            self, include_urls=include_urls, session=session, headers=headers
        )
        WikipediaInfoboxScraper.__init__(self, timeout=timeout)
        self.url: str = ""

    # ------------------------------
    # Publiczne API
    # ------------------------------

    def fetch(self, url: str) -> Dict[str, Any]:
        self.url = url
        base_url, fragment = (url.split("#", 1) + [None])[:2]
        self.url = base_url

        html = self._download()
        full_soup = BeautifulSoup(html, "html.parser")

        # 1) Filtr po kategoriach – jeśli to nie wygląda na tor / tor wyścigowy,
        #    nie dokładamy infoboksa, zostajemy przy tym co już mamy.
        if not self._is_circuit_like_article(full_soup):
            title = full_soup.title.get_text(strip=True) if full_soup.title else None
            return self._prune_nulls(
                {
                    "url": url,
                    "title": title,
                },
            )

        # 2) Jeśli mamy #fragment, zawężamy się do tej sekcji
        soup = full_soup
        if fragment:
            section = self._extract_section_by_id(full_soup, fragment)
            if section is not None:
                soup = section

        return self.parse_from_soup(soup)

    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """API bazowej klasy – deleguje do parse_from_soup."""
        return [self.parse_from_soup(soup)]

    def parse_from_soup(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Zwraca znormalizowany infobox + layouts (bez surowego `rows`)."""
        raw = super().parse_from_soup(soup)
        layout_records = self._parse_layout_sections(soup)
        return self._with_normalized(raw, layout_records)

    # ------------------------------
    # Pobieranie / sekcje / kategorie
    # ------------------------------

    def _download(self) -> str:
        if not self.url:
            raise ValueError("URL must be set before downloading")
        response = self.session.get(self.url, timeout=self.timeout)
        response.raise_for_status()
        return response.text

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

    def _extract_section_by_id(
        self, soup: BeautifulSoup, fragment: str
    ) -> Optional[BeautifulSoup]:
        """Zwraca pod-drzewo z daną sekcją (#id) lub None jeśli nie znaleziono."""
        span = soup.find(id=fragment)
        if not span:
            return None

        header = span.find_parent(["h1", "h2", "h3", "h4", "h5", "h6"])
        if not header:
            return None

        # Zbieramy header + wszystkie rodzeństwa aż do kolejnego nagłówka
        container = BeautifulSoup("<div></div>", "html.parser")
        root = container.div
        root.append(header)

        for sib in header.next_siblings:
            if isinstance(sib, Tag) and sib.name in [
                "h1",
                "h2",
                "h3",
                "h4",
                "h5",
                "h6",
            ]:
                break
            root.append(sib)

        return container
