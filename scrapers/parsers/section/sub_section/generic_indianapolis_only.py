from __future__ import annotations

from bs4 import Tag

from scrapers.parsers.list_element.indianapolis_constructors import (
    IndianapolisConstructorsListParser,
)
from scrapers.parsers.section.extraction_context import SectionExtractionContext
from scrapers.parsers.section.sub_section.base import SubSectionParser
from scrapers.parsers.section.types import SectionTreePayload


class GenericIndianapolisOnlySubSectionParser(SubSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self._list_parser = IndianapolisConstructorsListParser()

    def parse(
        self,
        element: Tag | list[Tag],
        *,
        context: SectionExtractionContext | None = None,
    ) -> SectionTreePayload:
        if isinstance(element, list):
            return self._parse_group(element, context=context)
        list_root = element.find(["ul", "ol"])
        if isinstance(list_root, Tag):
            return self._list_parser.parse(list_root)
        return self._parse_group(list(element.children), context=context)

    def _parse_group(
        self,
        elements: list,
        *,
        context: SectionExtractionContext | None = None,
    ) -> SectionTreePayload:
        _ = context
        for candidate in elements:
            if isinstance(candidate, Tag) and candidate.name in {"ul", "ol"}:
                return self._list_parser.parse(candidate)
        return {"items": []}


__all__ = ["GenericIndianapolisOnlySubSectionParser"]
