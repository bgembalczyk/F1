from __future__ import annotations

from typing import Any

from bs4 import Tag

from models.payload import WikiParsedPayload
from scrapers.parsers.mixins.wiki_element import WikiElementParserMixin
from scrapers.parsers.section.extraction_context import SectionExtractionContext
from scrapers.parsers.wiki.base import WikiParser
from scrapers.parsers.section.wiki.toolbox import SectionParserToolbox
from scrapers.parsers.section.wiki.toolbox import build_default_section_toolbox


class SubSubSubSectionParser(WikiElementParserMixin, WikiParser):
    @property
    def element_parsers(self):
        return self.toolbox.element_parsers

    def __init__(
        self,
        *,
        toolbox: SectionParserToolbox | None = None,
    ) -> None:
        self.toolbox = toolbox or build_default_section_toolbox()
        WikiElementParserMixin.__init__(
            self,
            element_parsers=self.toolbox.element_parsers,
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
