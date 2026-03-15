from typing import Any

from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser


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
        refs = [li.get_text(" ", strip=True) for li in element.find_all("li")]
        return {"references": refs}
