from bs4 import Tag

from models.data.parsed.paragraph import ParagraphParsedData
from scrapers.parsers.text_cleaning import extract_text
from scrapers.parsers.wiki.base import WikiParser


class ParagraphParser(WikiParser[Tag, ParagraphParsedData]):
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
