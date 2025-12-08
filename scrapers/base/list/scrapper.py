from abc import ABC
from typing import Optional, List, Dict, Any

from bs4 import BeautifulSoup, Tag

from scrapers.base.scraper import F1Scraper


class F1ListScraper(F1Scraper, ABC):
    """
    Scraper dla list (ul/ol) w konkretnej sekcji.

    Konfiguracja:
    - section_id  – id elementu <span id="..."> w nagłówku sekcji
    - record_key  – klucz w słowniku rekordu; jeżeli jest ustawiony, bazowa
      implementacja ``parse_item`` zwraca prosty słownik z nazwą elementu i
      (opcjonalnym) URL-em,
    - url_key     – klucz pod którym zapisywany jest pełny URL linku.
    """

    section_id: Optional[str] = None
    record_key: Optional[str] = None
    url_key: str = "url"

    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        root_list = self._find_list_root(soup)
        items: List[Dict[str, Any]] = []

        for li in root_list.find_all("li", recursive=False):
            rec = self.parse_item(li)
            if rec:
                items.append(rec)

        return items

    def _find_list_root(self, soup: BeautifulSoup) -> Tag:
        if self.section_id:
            heading = soup.find(id=self.section_id)
            if not heading:
                raise RuntimeError(f"Nie znaleziono sekcji o id={self.section_id!r}")

            # szukamy pierwszej listy (ul/ol) po nagłówku
            lst = heading.find_next(["ul", "ol"])
            if not lst:
                raise RuntimeError("Nie znaleziono listy w sekcji.")
            return lst

        # fallback: pierwsza lista na stronie
        lst = soup.find(["ul", "ol"])
        if not lst:
            raise RuntimeError("Nie znaleziono żadnej listy.")
        return lst

    def parse_item(self, li: Tag) -> Optional[Dict[str, Any]]:
        """Zamienia pojedynczy <li> na słownik."""

        if not self.record_key:
            raise NotImplementedError(
                "record_key nie jest zdefiniowany; zaimplementuj parse_item"
            )

        a = li.find("a")
        name = li.get_text(" ", strip=True)
        if not name:
            return None

        record: Dict[str, Any] = {self.record_key: name}
        if self.include_urls and a and a.has_attr("href"):
            record[self.url_key] = self._full_url(a["href"])

        return record
