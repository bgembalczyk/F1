from __future__ import annotations

from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.elements.figure import FigureParser
from scrapers.wiki.parsers.elements.infobox import InfoboxParser
from scrapers.wiki.parsers.elements.list_parser import ListParser
from scrapers.wiki.parsers.elements.navbox import NavBoxParser
from scrapers.wiki.parsers.elements.paragraph import ParagraphParser
from scrapers.wiki.parsers.elements.references_wrap import ReferencesWrapParser
from scrapers.wiki.parsers.elements.table import TableParser
from scrapers.wiki.parsers.result_model import TOP_SECTION_NAME
from scrapers.wiki.parsers.result_model import ParserResultItem
from scrapers.wiki.parsers.result_model import build_meta
from scrapers.wiki.parsers.result_model import to_legacy_element


def _split_into_parts(children: list[Tag], heading_class: str) -> list[tuple[str, list[Tag]]]:
    parts: list[tuple[str, list[Tag]]] = []
    current_name: str = TOP_SECTION_NAME
    current_elements: list[Tag] = []

    for child in children:
        if not isinstance(child, Tag):
            continue
        classes = child.get("class") or []
        if heading_class in classes:
            parts.append((current_name, current_elements))
            heading_tag = child.find(True, recursive=False)
            current_name = (
                heading_tag.get("id") or heading_tag.get_text(" ", strip=True)
                if heading_tag
                else TOP_SECTION_NAME
            )
            current_elements = []
        else:
            current_elements.append(child)

    parts.append((current_name, current_elements))
    return parts


class WikiElementParserMixin:
    def __init__(self) -> None:
        self.infobox_parser = InfoboxParser()
        self.paragraph_parser = ParagraphParser()
        self.figure_parser = FigureParser()
        self.list_parser = ListParser()
        self.table_parser = TableParser()
        self.navbox_parser = NavBoxParser()
        self.references_wrap_parser = ReferencesWrapParser()

    @staticmethod
    def _has_infobox_class(classes: Any) -> bool:
        if not classes:
            return False
        if isinstance(classes, str):
            classes = classes.split()
        try:
            return "infobox" in list(classes)
        except TypeError:
            return False

    def find_infobox(self, soup: BeautifulSoup) -> Tag | None:
        return soup.find("table", class_=self._has_infobox_class)

    def find_infoboxes(self, soup: BeautifulSoup) -> list[Tag]:
        return soup.find_all("table", class_=self._has_infobox_class)

    def parse_elements(
        self,
        elements: list[Tag],
        *,
        section_id: str,
        heading_id: str | None,
        heading_path: list[str],
    ) -> list[ParserResultItem]:
        result: list[ParserResultItem] = []
        for position, el in enumerate(elements):
            meta = build_meta(
                section_id=section_id,
                heading_id=heading_id,
                heading_path=heading_path,
                position=position,
            )
            parsed = self._parse_element(el, meta)
            if parsed is not None:
                result.append(parsed)
        return result

    def _parse_element(self, el: Tag, meta: dict[str, Any]) -> ParserResultItem | None:
        if el.name == "p":
            return self.paragraph_parser.parse(el, meta=meta)

        if el.name == "figure":
            return self.figure_parser.parse(el, meta=meta)

        if el.name == "ul":
            return self.list_parser.parse(el, meta=meta)

        if el.name == "table":
            classes = el.get("class") or []
            if "infobox" in classes:
                return self.infobox_parser.parse(el, meta=meta)
            if "wikitable" in classes:
                return self.table_parser.parse(el, meta=meta)

        if el.name == "div":
            classes = el.get("class") or []
            role = el.get("role")
            if role == "navigation" and "navbox" in classes:
                return self.navbox_parser.parse(el, meta=meta)
            if any("references-wrap" in c for c in classes):
                return self.references_wrap_parser.parse(el, meta=meta)

        return None


class SubSubSubSectionParser(WikiElementParserMixin, WikiParser):
    def __init__(self) -> None:
        WikiElementParserMixin.__init__(self)

    def parse(self, element: Tag) -> dict[str, Any]:
        return self.parse_group(list(element.children))

    def parse_group(
        self,
        elements: list,
        *,
        section_id: str = TOP_SECTION_NAME,
        heading_id: str | None = None,
        heading_path: list[str] | None = None,
    ) -> dict[str, Any]:
        tags = [c for c in elements if isinstance(c, Tag)]
        resolved_heading_path = heading_path or [section_id]
        items = self.parse_elements(
            tags,
            section_id=section_id,
            heading_id=heading_id,
            heading_path=resolved_heading_path,
        )
        return {
            "items": items,
            "elements": [to_legacy_element(item) for item in items],
        }
