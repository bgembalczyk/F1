from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from models.records.link import LinkRecord
from scrapers.base.helpers.links import normalize_links
from scrapers.base.helpers.url import normalize_url
from scrapers.wiki.parsers.elements.infobox import InfoboxParser


class InfoboxHtmlParser(InfoboxParser):
    """Parser HTML infoboxów z Wikipedii (tytuł, wiersze, linki)."""

    WIKIPEDIA_BASE = "https://en.wikipedia.org"

    def __init__(self, wikipedia_base: str | None = None) -> None:
        self.wikipedia_base = wikipedia_base or self.WIKIPEDIA_BASE

    def parse(self, soup: BeautifulSoup) -> dict[str, Any]:
        if isinstance(soup, Tag) and self.has_infobox_class(soup.get("class", [])):
            return self._parse_infobox(soup)
        infobox = self.find_infobox(soup)
        if infobox is None:
            return {"title": None, "rows": {}}

        return self._parse_infobox(infobox)

    def parse_element(self, element: Tag) -> dict[str, Any]:
        """Parsuje konkretny element tabeli infoboksa.

        Umożliwia przetworzenie pojedynczej tabeli infoboxu bez
        konieczności przeszukiwania całej strony. Jest to publiczny
        odpowiednik prywatnej metody ``_parse_infobox``.

        Args:
            element: Element <table class="infobox ..."> do sparsowania.

        Returns:
            Słownik z tytułem i wierszami infoboksa (wiersze zawierają tekst
            i linki).
        """
        return self._parse_infobox(element)

    @staticmethod
    def has_infobox_class(c) -> bool:
        """Sprawdza czy element zawiera klasę 'infobox'."""
        if not c:
            return False
        if isinstance(c, str):
            classes = c.split()
        else:
            # BeautifulSoup zwykle daje listę
            try:
                classes = list(c)
            except TypeError:
                return False
        return "infobox" in classes

    @staticmethod
    def find_infobox(soup: BeautifulSoup):
        """
        Znajduje <table> z klasą zawierającą 'infobox' w ramach przekazanego `soup`.

        Obsługuje zarówno:
        - class="infobox vcard"
        - class=["infobox", "vcard"]
        """
        return soup.find("table", class_=InfoboxHtmlParser.has_infobox_class)

    def _parse_infobox(self, table: Tag) -> dict[str, Any]:
        return self.parse_table_rows(table)

    def parse_row_value(self, value: Tag) -> dict[str, Any]:
        return {
            "text": value.get_text(" ", strip=True),
            "links": self.extract_links(value),
        }

    def extract_links(self, td) -> list[LinkRecord]:
        """
        Wyciąga wszystkie linki z komórki, pomijając linki do przypisów.
        """
        return normalize_links(
            td,
            full_url=lambda href: normalize_url(self.wikipedia_base, href),
            allow_local_anchors=False,
        )
