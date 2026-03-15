from typing import Any

from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.result_model import ParserMeta
from scrapers.wiki.parsers.result_model import build_result_item


class ListParser(WikiParser):
    def parse(self, element: Tag, meta: ParserMeta | None = None) -> dict[str, Any]:
        items = [li.get_text(" ", strip=True) for li in element.find_all("li", recursive=False)]
        return build_result_item("list", {"items": items}, meta or {})
