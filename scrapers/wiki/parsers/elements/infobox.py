from typing import Any

from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.types import InfoboxParsedData


class InfoboxParser(WikiParser[InfoboxParsedData]):
    """Parser infoboxów Wikipedii.

    Przetwarza tabelę: <table class="infobox vcard">
    """

    def parse(self, element: Tag) -> InfoboxParsedData:
        """Parsuje infobox Wikipedii.

        Args:
            element: Element <table class="infobox vcard">.

        Returns:
            Słownik z tytułem i wierszami infoboxa.
        """
        return self.parse_table_rows(element)

    def parse_table_rows(self, table: Tag) -> InfoboxParsedData:
        data: InfoboxParsedData = {"title": None, "rows": {}}

        caption = table.find("caption")
        if caption:
            data["title"] = caption.get_text(" ", strip=True)

        for tr in table.find_all("tr"):
            if tr.find_parent("table") is not table:
                continue
            header = tr.find("th", recursive=False)
            value = tr.find("td", recursive=False)
            if not header or not value:
                continue
            key = header.get_text(" ", strip=True)
            data["rows"][key] = self.parse_row_value(value)

        return data

    def parse_row_value(self, value: Tag) -> Any:
        return value.get_text(" ", strip=True)
