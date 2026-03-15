from typing import Any

from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.result_model import ParserMeta
from scrapers.wiki.parsers.result_model import build_result_item


class FigureParser(WikiParser):
    def parse(self, element: Tag, meta: ParserMeta | None = None) -> dict[str, Any]:
        caption_tag = element.find("figcaption")
        img_tag = element.find("img")
        payload = {
            "caption": caption_tag.get_text(" ", strip=True) if caption_tag else None,
            "src": img_tag.get("src") if img_tag else None,
        }
        return build_result_item("figure", payload, meta or {})
