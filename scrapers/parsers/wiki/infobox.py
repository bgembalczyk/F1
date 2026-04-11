from typing import Any
import warnings

from bs4 import Tag

from models.data.parsed.infobox import InfoboxParsedData
from scrapers.parsers.wiki.base import WikiParser


class WikiInfoboxElementParserBase(WikiParser[Tag, InfoboxParsedData]):
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


class InfoboxParser(InfoboxElementParser):
    pass


__all__ = ["InfoboxParser", "InfoboxParsedData"]
