from bs4 import Tag

from models.data.parsed.list import ListParsedData
from scrapers.parsers.text_cleaning import extract_text
from scrapers.parsers.wiki.base import WikiParser


class ListParser(WikiParser[Tag, ListParsedData]):
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
