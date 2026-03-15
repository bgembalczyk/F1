from __future__ import annotations

from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.elements.figure import FigureParser
from scrapers.wiki.parsers.elements.infobox import InfoboxParser
from scrapers.wiki.parsers.elements.list_parser import ListParser
from scrapers.wiki.parsers.elements.navbox import NavBoxParser
from scrapers.wiki.parsers.elements.paragraph import ParagrafParser
from scrapers.wiki.parsers.elements.references_wrap import ReferencesWrapParser
from scrapers.wiki.parsers.elements.table import TableParser

TOP_SECTION_NAME = "(Top)"


def _split_into_parts(
    children: list[Tag],
    heading_class: str,
) -> list[tuple[str, list[Tag]]]:
    """Dzieli listę elementów na części według nagłówków danego poziomu.

    Pierwsza część (przed pierwszym nagłówkiem) otrzymuje nazwę TOP_SECTION_NAME.
    Każda kolejna część jest otwierana przez div nagłówkowy i nosi nazwę
    zgodną z id nagłówka w headerze.

    Args:
        children: Lista elementów potomnych kontenera.
        heading_class: Klasa CSS identyfikująca nagłówki tego poziomu
            (np. "mw-heading2").

    Returns:
        Lista krotek (nazwa, lista_elementów).
    """
    parts: list[tuple[str, list[Tag]]] = []
    current_name: str = TOP_SECTION_NAME
    current_elements: list[Tag] = []

    for child in children:
        if not isinstance(child, Tag):
            continue
        classes = child.get("class") or []
        if heading_class in classes:
            parts.append((current_name, current_elements))
            heading_tag = child.find(True, recursive=False)
            current_name = (
                heading_tag.get("id") or heading_tag.get_text(" ", strip=True)
                if heading_tag
                else TOP_SECTION_NAME
            )
            current_elements = []
        else:
            current_elements.append(child)

    parts.append((current_name, current_elements))
    return parts


class WikiElementParserMixin:
    """Mixin dostarczający narzędzia do parsowania elementów HTML Wikipedii.

    Używany przez parsery sekcji wszystkich poziomów.
    Zawiera parsery dla typowych elementów HTML obecnych w artykułach Wikipedii:
    - InfoboxParser dla: <table class="infobox vcard">
    - ParagrafParser dla: <p>
    - FigureParser dla: <figure>
    - ListParser dla: <ul>
    - TableParser dla: <table class="wikitable">
    - NavBoxParser dla: <div role="navigation" class="navbox">
    - ReferencesWrapParser dla: divów z klasą zawierającą references-wrap

    Udostępnia też pomocnicze metody do wyszukiwania infoboxów w soup:
    - find_infobox(soup)   → pierwszy infobox jako Tag lub None
    - find_infoboxes(soup) → lista wszystkich infoboxów jako list[Tag]
    """

    def __init__(self) -> None:
        self.infobox_parser = InfoboxParser()
        self.paragraph_parser = ParagrafParser()
        self.figure_parser = FigureParser()
        self.list_parser = ListParser()
        self.table_parser = TableParser()
        self.navbox_parser = NavBoxParser()
        self.references_wrap_parser = ReferencesWrapParser()

    @staticmethod
    def _has_infobox_class(classes: Any) -> bool:
        """Sprawdza czy element zawiera klasę 'infobox'."""
        if not classes:
            return False
        if isinstance(classes, str):
            classes = classes.split()
        try:
            return "infobox" in list(classes)
        except TypeError:
            return False

    def find_infobox(self, soup: BeautifulSoup) -> Tag | None:
        """Zwraca pierwszą tabelę z klasą 'infobox' w podanym soup lub None."""
        return soup.find("table", class_=self._has_infobox_class)

    def find_infoboxes(self, soup: BeautifulSoup) -> list[Tag]:
        """Zwraca listę wszystkich tabel z klasą 'infobox' w podanym soup."""
        return soup.find_all("table", class_=self._has_infobox_class)

    def parse_elements(self, elements: list[Tag]) -> list[dict[str, Any]]:
        """Parsuje listę elementów HTML za pomocą odpowiednich narzędzi.

        Args:
            elements: Lista elementów HTML do sparsowania.

        Returns:
            Lista wyekstrahowanych danych dla każdego poznanego elementu.
        """
        result: list[dict[str, Any]] = []
        for el in elements:
            parsed = self._parse_element(el)
            if parsed is not None:
                result.append(parsed)
        return result

    def _parse_element(self, el: Tag) -> dict[str, Any] | None:
        """Wybiera właściwy parser dla danego elementu i parsuje go.

        Args:
            el: Element HTML do sparsowania.

        Returns:
            Sparsowane dane lub None jeśli element nie jest obsługiwany.
        """
        if el.name == "p":
            return {"type": "paragraph", "data": self.paragraph_parser.parse(el)}

        if el.name == "figure":
            return {"type": "figure", "data": self.figure_parser.parse(el)}

        if el.name == "ul":
            return {"type": "list", "data": self.list_parser.parse(el)}

        if el.name == "table":
            classes = el.get("class") or []
            if "infobox" in classes:
                return {"type": "infobox", "data": self.infobox_parser.parse(el)}
            if "wikitable" in classes:
                return {"type": "table", "data": self.table_parser.parse(el)}

        if el.name == "div":
            classes = el.get("class") or []
            role = el.get("role")
            if role == "navigation" and "navbox" in classes:
                return {"type": "navbox", "data": self.navbox_parser.parse(el)}
            if any("references-wrap" in c for c in classes):
                return {
                    "type": "references_wrap",
                    "data": self.references_wrap_parser.parse(el),
                }

        return None


class SubSubSubSectionParser(WikiElementParserMixin, WikiParser):
    """Parser podpodpodsekcji Wikipedii (poziom 5).

    Przetwarza fragment HTML między kolejnymi:
    <div class="mw-heading mw-heading5"><h5 id=...>

    Nie zagłębia się dalej – używa wyłącznie narzędzi elementarnych
    (InfoboxParser, ParagrafParser, FigureParser, ListParser, TableParser,
    NavBoxParser, ReferencesWrapParser).
    """

    def __init__(self) -> None:
        WikiElementParserMixin.__init__(self)

    def parse(self, element: Tag) -> dict[str, Any]:
        """Parsuje zawartość podpodpodsekcji.

        Args:
            element: Kontener zawierający elementy podpodpodsekcji.

        Returns:
            Słownik z listą sparsowanych elementów.
        """
        return self.parse_group(list(element.children))

    def parse_group(self, elements: list) -> dict[str, Any]:
        """Parsuje grupę elementów HTML.

        Args:
            elements: Lista elementów (potomków kontenera sekcji).

        Returns:
            Słownik z listą sparsowanych elementów.
        """
        tags = [c for c in elements if isinstance(c, Tag)]
        return {"elements": self.parse_elements(tags)}
