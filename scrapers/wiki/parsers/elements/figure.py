from typing import Any

from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.context import WikiParserContext


class FigureParser(WikiParser):
    """Parser elementów graficznych Wikipedii.

    Przetwarza element: <figure>
    """

    def parse(self, element: Tag, context: WikiParserContext | None = None) -> dict[str, Any]:
        """Parsuje element figure HTML.

        Args:
            element: Element <figure>.

        Returns:
            Słownik z podpisem i informacjami o obrazku.
        """
        caption_tag = element.find("figcaption")
        img_tag = element.find("img")
        return {
            "caption": caption_tag.get_text(" ", strip=True) if caption_tag else None,
            "src": img_tag.get("src") if img_tag else None,
        }
