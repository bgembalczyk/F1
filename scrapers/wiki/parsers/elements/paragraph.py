from typing import Any

from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.elements.text_cleaning import extract_text


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
        return {"text": extract_text(element) or ""}
