from typing import Any

from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.context import WikiParserContext


class InfoboxParser(WikiParser):
    """Parser infoboxów Wikipedii.

    Przetwarza tabelę: <table class="infobox vcard">
    """

    def parse(self, element: Tag, context: WikiParserContext | None = None) -> dict[str, Any]:
        """Parsuje infobox Wikipedii.

        Args:
            element: Element <table class="infobox vcard">.

        Returns:
            Słownik z tytułem i wierszami infoboxa.
        """
        data: dict[str, Any] = {"title": None, "rows": {}}

        caption = element.find("caption")
        if caption:
            data["title"] = caption.get_text(" ", strip=True)

        for tr in element.find_all("tr"):
            if tr.find_parent("table") is not element:
                continue
            header = tr.find("th", recursive=False)
            value = tr.find("td", recursive=False)
            if not header or not value:
                continue
            key = header.get_text(" ", strip=True)
            data["rows"][key] = value.get_text(" ", strip=True)

        return data
