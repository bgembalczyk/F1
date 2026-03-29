from __future__ import annotations

from typing import Any

from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.elements.mixin import WikiElementParserMixin
from scrapers.wiki.parsers.elements.parsers import WikiElementParsers
from scrapers.wiki.parsers.elements.parsers import build_default_wiki_element_parsers
from scrapers.wiki.parsers.sections.data_classes import SectionExtractionContext
from scrapers.wiki.parsers.types import WikiParsedPayload


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
