from bs4 import Tag

from models.data.parsed.paragraph import ParagraphParsedData
from scrapers.parsers.wiki.base import WikiParser
from scrapers.parsers.wiki.text_cleaning import extract_text


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
