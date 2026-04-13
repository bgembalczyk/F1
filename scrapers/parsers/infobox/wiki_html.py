from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from models.records.link import LinkRecord
from scrapers.helpers.links import normalize_links
from scrapers.helpers.url import normalize_url
from scrapers.parsers.contracts.wiki_elements import WikiInfoboxElementParserABC
from scrapers.parsers.infobox_element_parser import InfoboxElementParser


class WikiInfoboxHtmlParser(WikiInfoboxElementParserABC):
    """Parser HTML infoboxów z Wikipedii (tytuł, wiersze, linki)."""

    WIKIPEDIA_BASE = "https://en.wikipedia.org"

    def __init__(self, wikipedia_base: str | None = None) -> None:
        self.wikipedia_base = wikipedia_base or self.WIKIPEDIA_BASE
        self._element_parser = InfoboxElementParser()

    def parse(self, fragment: BeautifulSoup) -> dict[str, Any]:
        return self.parse_fragment(fragment)

    def parse_fragment(self, fragment: BeautifulSoup) -> dict[str, Any]:
        if isinstance(fragment, Tag) and fragment.name == "table":
            return self.parse_group(fragment)
        infobox = self.find_infobox(fragment)
        if infobox is None:
            return {"title": None, "rows": {}}

        return self.parse_group(infobox)

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
        return self.parse_group(element)

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
        return soup.find("table", class_=WikiInfoboxHtmlParser.has_infobox_class)

    def parse_group(self, table: Tag) -> dict[str, Any]:
        data: dict[str, Any] = {"title": None, "rows": {}}
        caption = table.find("caption")
        if caption:
            data["title"] = caption.get_text(" ", strip=True)

        for tr in table.find_all("tr"):
            if tr.find_parent("table") is not table:
                continue
            header = tr.find("th", recursive=False)
            value = tr.find("td", recursive=False)
            if not header or not value:
                continue
            key = header.get_text(" ", strip=True)
            data["rows"][key] = self.parse_row(value)
        return data

    def parse_row(self, value: Tag) -> dict[str, Any]:
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


__all__ = ["WikiInfoboxHtmlParser"]
