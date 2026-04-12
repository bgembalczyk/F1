from typing import Any

from bs4 import Tag

from models.data.parsed.html_elements import InfoboxElementData
from scrapers.parsers.contracts.wiki_elements import WikiInfoboxElementParserABC
from scrapers.parsers.wiki.parser_mixins import HeaderNormalizationMixin
from scrapers.parsers.wiki.parser_mixins import TableCellExtractionMixin


class InfoboxElementParser(
    TableCellExtractionMixin,
    HeaderNormalizationMixin,
    WikiInfoboxElementParserABC,
):
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
            cells = self.extract_row_cells(tr)
            if len(cells) < 2:
                continue
            header, value = cells[0], cells[1]
            key = self.normalize_header(header.get_text(" ", strip=True))
            data["rows"][key] = self.parse_row_value(value)
        return data

    def parse_row_value(self, value: Tag) -> Any:
        return value.get_text(" ", strip=True)
