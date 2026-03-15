from typing import Any

from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.context import WikiParserContext


class ParagraphParser(WikiParser):
    """Parser akapitów Wikipedii.

    Przetwarza element: <p>
    """

    def parse(self, element: Tag, context: WikiParserContext | None = None) -> dict[str, Any]:
        """Parsuje akapit HTML.

        Args:
            element: Element <p>.

        Returns:
            Słownik z tekstem akapitu.
        """
        return {"text": element.get_text(" ", strip=True)}


# Alias przejściowy dla kompatybilności wstecznej.
ParagrafParser = ParagraphParser
