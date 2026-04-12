from __future__ import annotations

from typing import Any

from bs4 import Tag

from models.payload import WikiParsedPayload
from scrapers.parsers.mixins.wiki.element import WikiElementParsingMixin
from scrapers.parsers.section.extraction_context import SectionExtractionContext
from scrapers.parsers.section.toolbox import SectionParserToolbox
from scrapers.parsers.section.toolbox import build_default_section_toolbox
from scrapers.parsers.wiki.base import WikiParser
from scrapers.parsers.wiki.element import WikiElementSet
from scrapers.parsers.wiki.element import build_wikipedia_element_registry


class SubSubSubSectionParser(WikiElementParsingMixin, WikiParser):
    @property
    def element_parsers(self):
        return self.toolbox.element_parsers

    def __init__(
        self,
        *,
        toolbox: SectionParserToolbox | None = None,
        element_parsers: WikiElementSet | None = None,
    ) -> None:
        self.toolbox = toolbox or build_default_section_toolbox()
        effective_parsers = element_parsers if element_parsers is not None else self.toolbox.element_parsers
        # Rebuild registry when element_parsers override is provided, so rules
        # use the overridden parsers (e.g. stubs injected in tests).
        if element_parsers is not None:
            effective_registry = build_wikipedia_element_registry(parsers=effective_parsers)
        else:
            effective_registry = self.toolbox.element_registry
        WikiElementParsingMixin.__init__(
            self,
            element_parsers=effective_parsers,
            element_registry=effective_registry,
        )

    def parse(
        self,
        element: Tag | list[Tag],
        *,
        context: SectionExtractionContext | None = None,
    ) -> dict[str, Any]:
        if isinstance(element, Tag):
            return self._parse_group(list(element.children), context=context)
        return self._parse_group(element, context=context)

    def parse_group(
        self,
        elements: list,
        *,
        context: SectionExtractionContext | None = None,
    ) -> dict[str, list[WikiParsedPayload]]:
        """Public interface for parsing a flat list of elements into the leaf section dict."""
        return self._parse_group(elements, context=context)

    def _parse_group(
        self,
        elements: list,
        *,
        context: SectionExtractionContext | None = None,
    ) -> dict[str, list[WikiParsedPayload]]:
        section_context = context or SectionExtractionContext()
        tags = [c for c in elements if isinstance(c, Tag)]
        return {
            "elements": self.parse_elements(tags, section_context=section_context)
        }


__all__ = ["SubSubSubSectionParser"]
