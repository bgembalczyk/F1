from abc import ABC
from typing import Optional

from bs4 import BeautifulSoup, Tag

from scrapers.base.errors import ScraperNotFoundError
from scrapers.base.helpers.html_utils import find_section_elements
from scrapers.base.ABC import F1Scraper
from scrapers.base.types import ExportableRecord


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

    def _parse_soup(self, soup: BeautifulSoup) -> list[ExportableRecord]:
        root_list = self._find_list_root(soup)
        items: list[ExportableRecord] = []

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
            raise ScraperNotFoundError("Nie znaleziono listy w sekcji.")

        raise ScraperNotFoundError("Nie znaleziono żadnej listy.")

    def parse_item(self, li: Tag) -> Optional[ExportableRecord]:
        """Zamienia pojedynczy <li> na słownik."""

        if not self.record_key:
            raise NotImplementedError(
                "record_key nie jest zdefiniowany; zaimplementuj parse_item"
            )

        a = li.find("a")
        name = li.get_text(" ", strip=True)
        if not name:
            return None

        record: dict[str, object] = {self.record_key: name}
        if self.include_urls and a and a.has_attr("href"):
            record[self.url_key] = self._full_url(a["href"])

        return record
