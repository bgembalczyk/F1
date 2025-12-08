from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

from bs4 import BeautifulSoup, Tag

from scrapers.base.helpers.utils import find_section_elements
from scrapers.base.scraper import F1Scraper


class F1ListScraper(F1Scraper, ABC):
    """
    Scraper dla list (ul/ol) w konkretnej sekcji.

    Konfiguracja:
    - section_id  – id elementu <span id="..."> w nagłówku sekcji
    """

    section_id: Optional[str] = None

    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        root_list = self._find_list_root(soup)
        items: List[Dict[str, Any]] = []

        for li in root_list.find_all("li", recursive=False):
            rec = self.parse_item(li)
            if rec:
                items.append(rec)

        return items

    def _find_list_root(self, soup: BeautifulSoup) -> Tag:
        candidate_lists = find_section_elements(soup, self.section_id, ["ul", "ol"])

        if candidate_lists:
            return candidate_lists[0]

        if self.section_id:
            raise RuntimeError("Nie znaleziono listy w sekcji.")

        raise RuntimeError("Nie znaleziono żadnej listy.")

    @abstractmethod
    def parse_item(self, li: Tag) -> Optional[Dict[str, Any]]:
        """Zamienia pojedynczy <li> na słownik."""
        raise NotImplementedError
