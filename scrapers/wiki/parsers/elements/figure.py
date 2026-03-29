from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.elements.text_cleaning import extract_text
from scrapers.wiki.parsers.types import FigureParsedData


class FigureParser(WikiParser[FigureParsedData]):
    """Parser elementów graficznych Wikipedii.

    Przetwarza element: <figure>
    """

    def parse(self, element: Tag) -> FigureParsedData:
        """Parsuje element figure HTML.

        Args:
            element: Element <figure>.

        Returns:
            Słownik z podpisem i informacjami o obrazku.
        """
        caption_tag = element.find("figcaption")
        img_tag = element.find("img")
        src = img_tag.get("src") if img_tag else None
        if not isinstance(src, str):
            src = None
        return {
            "caption": extract_text(caption_tag),
            "src": src,
        }
