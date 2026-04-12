from typing import Any

from bs4 import Tag

from models.data.parsed.html_elements import InfoboxElementData
from scrapers.parsers.wiki.wiki_element_parser_abc import WikiInfoboxElementParserABC


class InfoboxElementParser(WikiInfoboxElementParserABC):
    def parse(self, raw: Tag) -> InfoboxElementData:
        return self.parse_table_rows(raw)

    def parse_table_rows(self, table: Tag) -> InfoboxElementData:
        data: InfoboxElementData = {"title": None, "rows": {}}
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
