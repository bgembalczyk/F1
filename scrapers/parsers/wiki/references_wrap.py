from bs4 import Tag

from models.data.parsed.references_wrap import ReferencesWrapParsedData
from scrapers.parsers.text_cleaning import extract_text
from scrapers.parsers.wiki.base import WikiParser


class ReferencesWrapParser(WikiParser[Tag, ReferencesWrapParsedData]):
    """Parser sekcji przypisów Wikipedii.

    Przetwarza divy z klasą zawierającą 'references-wrap'.
    """
    element_type = "references"

    def parse(self, element: Tag) -> ReferencesWrapParsedData:
        """Parsuje sekcję przypisów HTML.

        Args:
            element: Element div z klasą zawierającą 'references-wrap'.

        Returns:
            Słownik z listą przypisów.
        """
        refs = [extract_text(li) or "" for li in element.find_all("li")]
        return {"references": refs}
