from typing import Any

from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.result_model import ParserMeta
from scrapers.wiki.parsers.result_model import build_result_item


class ReferencesWrapParser(WikiParser):
    def parse(self, element: Tag, meta: ParserMeta | None = None) -> dict[str, Any]:
        refs = [li.get_text(" ", strip=True) for li in element.find_all("li")]
        return build_result_item("references_wrap", {"references": refs}, meta or {})
