from typing import Any

from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.elements.text_cleaning import extract_text


class FigureParser(WikiParser):
    """Parser elementów graficznych Wikipedii.

    Przetwarza element: <figure>
    """

    def parse(self, element: Tag) -> dict[str, Any]:
        """Parsuje element figure HTML.

        Args:
            element: Element <figure>.

        Returns:
            Słownik z podpisem i informacjami o obrazku.
        """
        caption_tag = element.find("figcaption")
        img_tag = element.find("img")
        return {
            "caption": extract_text(caption_tag),
            "src": img_tag.get("src") if img_tag else None,
        }
