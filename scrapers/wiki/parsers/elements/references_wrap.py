from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.elements.text_cleaning import extract_text
from scrapers.wiki.parsers.types import ReferencesWrapParsedData


class ReferencesWrapParser(WikiParser[ReferencesWrapParsedData]):
    """Parser sekcji przypisów Wikipedii.

    Przetwarza divy z klasą zawierającą 'references-wrap'.
    """

    def parse(self, element: Tag) -> ReferencesWrapParsedData:
        """Parsuje sekcję przypisów HTML.

        Args:
            element: Element div z klasą zawierającą 'references-wrap'.

        Returns:
            Słownik z listą przypisów.
        """
        refs = [extract_text(li) or "" for li in element.find_all("li")]
        return {"references": refs}
