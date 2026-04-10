from bs4 import Tag

from models.data.parsed.list import ListParsedData
from scrapers.parsers.wiki.base import WikiParser
from scrapers.parsers.wiki.text_cleaning import extract_text


class ListParser(WikiParser[ListParsedData]):
    """Parser list nieuporządkowanych Wikipedii.

    Przetwarza element: <ul>
    """

    def parse(self, element: Tag) -> ListParsedData:
        """Parsuje listę nieuporządkowaną HTML.

        Args:
            element: Element <ul>.

        Returns:
            Słownik z listą elementów.
        """
        items = [
            extract_text(li) or "" for li in element.find_all("li", recursive=False)
        ]
        return {"items": items}
