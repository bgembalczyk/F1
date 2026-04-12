from __future__ import annotations

from typing import Any

from bs4 import Tag

from scrapers.parsers.nested_child import NestedChildParser
from scrapers.parsers.section.extraction_context import SectionExtractionContext
from scrapers.parsers.section.toolbox import SectionParserToolbox
from scrapers.parsers.wiki.recursive import RecursiveSectionParser
from scrapers.parsers.wiki.wiki_section_parser_abc import WikiSectionParserABC


class BaseNestedSectionParser(RecursiveSectionParser, WikiSectionParserABC):
    heading_class: str
    output_key: str

    def __init__(
        self,
        *,
        child_parser: NestedChildParser,
        toolbox: SectionParserToolbox | None = None,
    ) -> None:
        super().__init__(
            heading_class=self.heading_class,
            output_key=self.output_key,
            child_parser=child_parser,
            toolbox=toolbox,
        )

    def parse(
        self,
        element: Tag | list[Tag],
        *,
        context: SectionExtractionContext | None = None,
    ) -> dict[str, Any]:
        return super().parse(element, context=context)


__all__ = [
    "NestedChildParser",
    "BaseNestedSectionParser",
]
