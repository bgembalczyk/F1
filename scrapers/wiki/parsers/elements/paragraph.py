from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.elements.text_cleaning import extract_text
from scrapers.wiki.parsers.types import ParagraphParsedData


class ParagraphParser(WikiParser[ParagraphParsedData]):
    """Parser akapitów Wikipedii.

    Przetwarza element: <p>
    """

    def parse(self, element: Tag) -> ParagraphParsedData:
        """Parsuje akapit HTML.

        Args:
            element: Element <p>.

        Returns:
            Słownik z tekstem akapitu.
        """
        return {"text": extract_text(element) or ""}
