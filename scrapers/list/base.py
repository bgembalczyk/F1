from abc import ABC

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.errors.category import ErrorCategory
from scrapers.errors.not_found import ScraperNotFoundError
from scrapers.helpers.html_utils import find_section_elements
from scrapers.scraper_wiki import WikiScraper
from scrapers.types import ExportableRecord


class ListScraper(WikiScraper, ABC):
    """
    Scraper dla list (ul/ol) w konkretnej sekcji.

    Konfiguracja:
    - section_id  - id elementu <span id="..."> w nagłówku sekcji
    - record_key  - klucz w słowniku rekordu; jeżeli jest ustawiony, bazowa
      implementacja ``parse_item`` zwraca prosty słownik z nazwą elementu i
      (opcjonalnym) URL-em,
    - url_key     - klucz pod którym zapisywany jest pełny URL linku.
    """

    scraper_kind: str = "list"

    section_id: str | None = None
    record_key: str | None = None
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
        return self._find_first_in_section(
            soup,
            section_id=self.section_id,
            tags=["ul", "ol"],
            missing_with_section_msg="Nie znaleziono listy w sekcji.",
            missing_global_msg="Nie znaleziono żadnej listy.",
        )

    def _find_first_in_section(
        self,
        soup: BeautifulSoup,
        *,
        section_id: str | None,
        tags: list[str],
        class_name: str | None = None,
        missing_with_section_msg: str,
        missing_global_msg: str,
    ) -> Tag:
        kwargs = {"class_": class_name} if class_name else {}
        candidate_elements = find_section_elements(soup, section_id, tags, **kwargs)
        if candidate_elements:
            return candidate_elements[0]

        if section_id:
            raise ScraperNotFoundError(
                missing_with_section_msg,
                category=ErrorCategory.PARSE,
            )
        raise ScraperNotFoundError(missing_global_msg)

    def parse_item(self, li: Tag) -> ExportableRecord | None:
        """Zamienia pojedynczy <li> na słownik."""

        if not self.record_key:
            msg = "record_key nie jest zdefiniowany; zaimplementuj parse_item"
            raise NotImplementedError(
                msg,
            )

        a = li.find("a")
        name = li.get_text(" ", strip=True)
        if not name:
            return None

        record: dict[str, object] = {self.record_key: name}
        if self.include_urls and a and a.has_attr("href"):
            record[self.url_key] = self._full_url(a["href"])

        return record

    """
    Scraper dla list (ul/ol) w konkretnej sekcji.

    Konfiguracja:
    - section_id  - id elementu <span id="..."> w nagłówku sekcji
    - record_key  - klucz w słowniku rekordu; jeżeli jest ustawiony, bazowa
      implementacja ``parse_item`` zwraca prosty słownik z nazwą elementu i
      (opcjonalnym) URL-em,
    - url_key     - klucz pod którym zapisywany jest pełny URL linku.
    """

    scraper_kind: str = "list"

    section_id: str | None = None
    record_key: str | None = None
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
        return self._find_first_in_section(
            soup,
            section_id=self.section_id,
            tags=["ul", "ol"],
            missing_with_section_msg="Nie znaleziono listy w sekcji.",
            missing_global_msg="Nie znaleziono żadnej listy.",
        )

    def parse_item(self, li: Tag) -> ExportableRecord | None:
        """Zamienia pojedynczy <li> na słownik."""

        if not self.record_key:
            msg = "record_key nie jest zdefiniowany; zaimplementuj parse_item"
            raise NotImplementedError(
                msg,
            )

        a = li.find("a")
        name = li.get_text(" ", strip=True)
        if not name:
            return None

        record: dict[str, object] = {self.record_key: name}
        if self.include_urls and a and a.has_attr("href"):
            record[self.url_key] = self._full_url(a["href"])

        return record
