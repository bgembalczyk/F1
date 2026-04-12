from __future__ import annotations

from typing import Any

from scrapers.parsers.nested_child import NestedChildParser
from scrapers.parsers.section.toolbox import SectionParserToolbox
from scrapers.parsers.wiki.recursive import RecursiveSectionParser


class BaseNestedSectionParser(RecursiveSectionParser):
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

__all__ = [
    "NestedChildParser",
    "BaseNestedSectionParser",
]
