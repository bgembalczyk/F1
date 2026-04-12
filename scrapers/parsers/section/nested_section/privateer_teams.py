from __future__ import annotations

from bs4 import Tag

from scrapers.parsers.contracts.wiki_elements import WikiListElementParserABC
from scrapers.parsers.section.extraction_context import SectionExtractionContext
from scrapers.parsers.section.nested_section.base import NestedWikiSectionParser
from scrapers.parsers.section.types import SectionTreePayload
from scrapers.parsers.wiki.privateer_teams_list import PrivateerTeamsListParser


class PrivateerTeamsSectionParser(NestedWikiSectionParser):
    def __init__(self, *, list_parser: WikiListElementParserABC | None = None) -> None:
        super().__init__()
        self._list_parser = list_parser or PrivateerTeamsListParser()

    def parse(
        self,
        element: Tag | list[Tag],
        *,
        context: SectionExtractionContext | None = None,
    ) -> SectionTreePayload:
        if isinstance(element, Tag):
            if element.name in {"ul", "ol"}:
                return self._list_parser.parse(element)
            list_root = element.find(["ul", "ol"])
            if isinstance(list_root, Tag):
                return self._list_parser.parse(list_root)
            return self._parse_group(list(element.children), context=context)
        return self._parse_group(element, context=context)

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
