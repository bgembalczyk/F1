from typing import Any

from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.result_model import ParserMeta
from scrapers.wiki.parsers.result_model import build_result_item


class ParagraphParser(WikiParser):
    def parse(self, element: Tag, meta: ParserMeta | None = None) -> dict[str, Any]:
        payload = {"text": element.get_text(" ", strip=True)}
        return build_result_item("paragraph", payload, meta or {})


ParagrafParser = ParagraphParser
