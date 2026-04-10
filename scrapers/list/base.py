from abc import ABC

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.mixins.section_traversal import SectionTraversalMixin
from scrapers.types import ExportableRecord
from scrapers.wiki.scraper_wiki import WikiScraper


class ListScraper(SectionTraversalMixin, WikiScraper, ABC):
    """
    Scraper dla list (ul/ol) w konkretnej sekcji.

    Konfiguracja:
    - section_id  - id elementu <span id="..."> w nagłówku sekcji
    - record_key  - klucz w słowniku rekordu; jeżeli jest ustawiony, bazowa
      implementacja ``parse_item`` zwraca prosty słownik z nazwą elementu i
      (opcjonalnym) URL-em,
    - url_key     - klucz pod którym zapisywany jest pełny URL linku.
    """

    FAMILY_KIND = "list"
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
