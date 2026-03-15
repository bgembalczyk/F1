from typing import Any

from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser


class ParagraphParser(WikiParser):
    """Parser akapitów Wikipedii.

    Przetwarza element: <p>
    """

    def parse(self, element: Tag) -> dict[str, Any]:
        """Parsuje akapit HTML.

        Args:
            element: Element <p>.

        Returns:
            Słownik z tekstem akapitu.
        """
        return {"text": element.get_text(" ", strip=True)}


# Alias przejściowy dla kompatybilności wstecznej.
ParagrafParser = ParagraphParser
