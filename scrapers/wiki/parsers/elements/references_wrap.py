from typing import Any

from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.elements.text_cleaning import extract_text


class ReferencesWrapParser(WikiParser):
    """Parser sekcji przypisów Wikipedii.

    Przetwarza divy z klasą zawierającą 'references-wrap'.
    """

    def parse(self, element: Tag) -> dict[str, Any]:
        """Parsuje sekcję przypisów HTML.

        Args:
            element: Element div z klasą zawierającą 'references-wrap'.

        Returns:
            Słownik z listą przypisów.
        """
        refs = [extract_text(li) or "" for li in element.find_all("li")]
        return {"references": refs}
