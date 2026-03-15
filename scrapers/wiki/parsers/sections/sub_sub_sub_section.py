from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.elements.figure import FigureParser
from scrapers.wiki.parsers.elements.infobox import InfoboxParser
from scrapers.wiki.parsers.elements.list_parser import ListParser
from scrapers.wiki.parsers.elements.navbox import NavBoxParser
from scrapers.wiki.parsers.elements.paragraph import ParagraphParser
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
    - ParagraphParser dla: <p>
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
        self.paragraph_parser = ParagraphParser()
        self.figure_parser = FigureParser()
        self.list_parser = ListParser()
        self.table_parser = TableParser()
        self.navbox_parser = NavBoxParser()
        self.references_wrap_parser = ReferencesWrapParser()
        self._parser_rules: list[ParserRule] = []
        self._register_default_parser_rules()

    @staticmethod
    def _get_classes(el: Tag) -> list[str]:
        """Zwraca klasy elementu HTML jako listę stringów."""
        classes = el.get("class") or []
        if isinstance(classes, str):
            return classes.split()
        return list(classes)

    def register_parser_rule(
        self,
        *,
        predicate: Callable[[Tag], bool],
        parser: Callable[[Tag], Any],
        result_type: str,
        priority: int | None = None,
    ) -> None:
        """Rejestruje regułę parsowania elementów HTML.

        Reguły są sprawdzane w kolejności rejestracji.
        Parametr ``priority`` pozwala wstawić regułę pod konkretny indeks.
        """
        rule = ParserRule(predicate=predicate, parser=parser, result_type=result_type)
        if priority is None:
            self._parser_rules.append(rule)
            return
        index = max(0, min(priority, len(self._parser_rules)))
        self._parser_rules.insert(index, rule)

    def _register_default_parser_rules(self) -> None:
        """Rejestruje domyślne reguły parsowania Wikipedii."""
        self.register_parser_rule(
            predicate=lambda el: el.name == "p",
            parser=self.paragraph_parser.parse,
            result_type="paragraph",
        )
        self.register_parser_rule(
            predicate=lambda el: el.name == "figure",
            parser=self.figure_parser.parse,
            result_type="figure",
        )
        self.register_parser_rule(
            predicate=lambda el: el.name == "ul",
            parser=self.list_parser.parse,
            result_type="list",
        )
        self.register_parser_rule(
            predicate=lambda el: el.name == "table"
            and "infobox" in self._get_classes(el),
            parser=self.infobox_parser.parse,
            result_type="infobox",
        )
        self.register_parser_rule(
            predicate=lambda el: el.name == "table"
            and "wikitable" in self._get_classes(el),
            parser=self.table_parser.parse,
            result_type="table",
        )
        self.register_parser_rule(
            predicate=lambda el: el.name == "div"
            and el.get("role") == "navigation"
            and "navbox" in self._get_classes(el),
            parser=self.navbox_parser.parse,
            result_type="navbox",
        )
        self.register_parser_rule(
            predicate=lambda el: el.name == "div"
            and any("references-wrap" in c for c in self._get_classes(el)),
            parser=self.references_wrap_parser.parse,
            result_type="references_wrap",
        )

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
        for rule in self._parser_rules:
            if rule.predicate(el):
                return {"type": rule.result_type, "data": rule.parser(el)}

        return None


@dataclass(frozen=True)
class ParserRule:
    """Pojedyncza reguła mapowania elementu HTML na parser wynikowy."""

    predicate: Callable[[Tag], bool]
    parser: Callable[[Tag], Any]
    result_type: str


class SubSubSubSectionParser(WikiElementParserMixin, WikiParser):
    """Parser podpodpodsekcji Wikipedii (poziom 5).

    Przetwarza fragment HTML między kolejnymi:
    <div class="mw-heading mw-heading5"><h5 id=...>

    Nie zagłębia się dalej – używa wyłącznie narzędzi elementarnych
    (InfoboxParser, ParagraphParser, FigureParser, ListParser, TableParser,
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
