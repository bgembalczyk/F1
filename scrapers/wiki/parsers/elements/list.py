from typing import Any

from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.elements.text_cleaning import extract_text


class ListParser(WikiParser):
    """Parser list nieuporządkowanych Wikipedii.

    Przetwarza element: <ul>
    """

    def parse(self, element: Tag) -> dict[str, Any]:
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
