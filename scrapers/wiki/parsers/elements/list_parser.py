from typing import Any

from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.context import WikiParserContext


class ListParser(WikiParser):
    """Parser list nieuporządkowanych Wikipedii.

    Przetwarza element: <ul>
    """

    def parse(self, element: Tag, context: WikiParserContext | None = None) -> dict[str, Any]:
        """Parsuje listę nieuporządkowaną HTML.

        Args:
            element: Element <ul>.

        Returns:
            Słownik z listą elementów.
        """
        items = [
            li.get_text(" ", strip=True)
            for li in element.find_all("li", recursive=False)
        ]
        return {"items": items}
