from typing import Any

from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.result_model import ParserMeta
from scrapers.wiki.parsers.result_model import build_result_item


class NavBoxParser(WikiParser):
    def parse(self, element: Tag, meta: ParserMeta | None = None) -> dict[str, Any]:
        title_tag = element.find(class_="navbox-title")
        title = title_tag.get_text(" ", strip=True) if title_tag else None
        links = [
            {"text": a.get_text(" ", strip=True), "href": a.get("href")}
            for a in element.find_all("a")
            if a.get("href")
        ]
        return build_result_item("navbox", {"title": title, "links": links}, meta or {})
