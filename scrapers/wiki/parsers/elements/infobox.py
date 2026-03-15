from typing import Any

from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.result_model import ParserMeta
from scrapers.wiki.parsers.result_model import build_result_item


class InfoboxParser(WikiParser):
    def parse(self, element: Tag, meta: ParserMeta | None = None) -> dict[str, Any]:
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

        return build_result_item("infobox", data, meta or {})
