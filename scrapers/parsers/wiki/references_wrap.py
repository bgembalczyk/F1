from bs4 import Tag

from models.data.parsed.references_wrap import ReferencesWrapParsedData
from scrapers.parsers.parser_abc import ParserABC
from scrapers.text_cleaning import extract_text


class ReferencesWrapParser(ParserABC[Tag, ReferencesWrapParsedData]):
    """Parser sekcji przypisów Wikipedii.

    Przetwarza divy z klasą zawierającą 'references-wrap'.
    """

    element_type = "references_wrap"

    def parse(self, element: Tag) -> ReferencesWrapParsedData:
        """Parsuje sekcję przypisów HTML.

        Args:
            element: Element div z klasą zawierającą 'references-wrap'.

        Returns:
            Słownik z listą przypisów.
        """
        refs = [extract_text(li) or "" for li in element.find_all("li")]
        return {"references": refs}
