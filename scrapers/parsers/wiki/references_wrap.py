from bs4 import Tag

from models.data.parsed.references_wrap import ReferencesWrapParsedData
from scrapers.parsers.wiki.base import WikiParser
from scrapers.parsers.wiki.text_cleaning import extract_text


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
