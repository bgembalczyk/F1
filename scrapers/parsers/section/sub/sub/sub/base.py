from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from bs4 import Tag

from scrapers.parsers.section.wiki.data_classes import SectionExtractionContext
from scrapers.parsers.wiki.base import WikiParser
from scrapers.parsers.wiki.elements.mixin import WikiElementParserMixin
from scrapers.parsers.wiki.elements.parsers import WikiElementParsers
from scrapers.parsers.wiki.elements.parsers import build_default_wiki_element_parsers
from scrapers.parsers.wiki.types import WikiParsedPayload


class SubSubSubSectionParser(WikiElementParserMixin, WikiParser):
    def __init__(
        self,
        *,
        element_parsers: WikiElementParsers | None = None,
    ) -> None:
        WikiElementParserMixin.__init__(
            self,
            element_parsers=element_parsers or build_default_wiki_element_parsers(),
        )

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
    ) -> dict[str, list[WikiParsedPayload]]:
        section_context = context or SectionExtractionContext()
        tags = [c for c in elements if isinstance(c, Tag)]
        return {
            "elements": self.parse_elements(tags, section_context=section_context),
        }


__all__ = ["SubSubSubSectionParser"]
