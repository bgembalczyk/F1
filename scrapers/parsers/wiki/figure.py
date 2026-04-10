from bs4 import Tag

from models.data.parsed.figure import FigureParsedData
from scrapers.parsers.wiki.base import WikiParser
from scrapers.parsers.wiki.text_cleaning import extract_text


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
