from __future__ import annotations

from typing import Any

from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.elements.mixin import WikiElementParserMixin
from scrapers.wiki.parsers.sections.data_classes import SectionExtractionContext


class SubSubSubSectionParser(WikiElementParserMixin, WikiParser):
    def __init__(self) -> None:
        WikiElementParserMixin.__init__(self)

    def parse(
        self,
        element: Tag,
        *,
        context: SectionExtractionContext | None = None,
    ) -> dict[str, Any]:
        return self.parse_group(list(element.children), context=context)

    def parse_group(
        self,
        elements: list,
        *,
        context: SectionExtractionContext | None = None,
    ) -> dict[str, Any]:
        section_context = context or SectionExtractionContext()
        tags = [c for c in elements if isinstance(c, Tag)]
        return {
            "elements": self.parse_elements(tags, section_context=section_context),
        }
