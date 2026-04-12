from __future__ import annotations

from typing import Any

from bs4 import Tag

from scrapers.parsers.privateer_teams_list import PrivateerTeamsListParser
from scrapers.parsers.wiki.nested_wiki import NestedWikiSectionParser
from scrapers.parsers.wiki.families import WikiListParserABC




class PrivateerTeamsSectionParser(NestedWikiSectionParser):
    def __init__(self, *, list_parser: WikiListParserABC | None = None) -> None:
        super().__init__()
        self._list_parser = list_parser or PrivateerTeamsListParser()

    def parse(self, element: Tag, *_args: Any, **_kwargs: Any) -> dict[str, Any]:
        if element.name in {"ul", "ol"}:
            return self._list_parser.parse(element)

        list_root = element.find(["ul", "ol"])
        if isinstance(list_root, Tag):
            return self._list_parser.parse(list_root)
        return self._parse_group(list(element.children), *_args, **_kwargs)

    def _parse_group(
        self,
        elements: list,
        *_args: Any,
        **_kwargs: Any,
    ) -> dict[str, Any]:
        for candidate in elements:
            if isinstance(candidate, Tag) and candidate.name in {"ul", "ol"}:
                return self._list_parser.parse(candidate)
        return {"items": []}
