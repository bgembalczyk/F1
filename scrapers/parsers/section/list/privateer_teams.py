from __future__ import annotations

import re
from typing import Any

from bs4 import Tag

from models.services.season import parse_seasons
from scrapers.helpers.text import clean_wiki_text
from scrapers.parsers.section.protocol import SectionParser
from scrapers.parsers.wiki.element_list import WikiListElementParser
from scrapers.parsers.wiki.families import WikiListHtmlParserABC


class PrivateerTeamsListParser(WikiListElementParser):
    def parse(self, element: Tag) -> dict[str, list[dict[str, Any]]]:
        items: list[dict[str, Any]] = []
        for li in element.find_all("li", recursive=False):
            row = self._parse_item(li)
            if row is not None:
                items.append(row)
        return {"items": items}

    @staticmethod
    def _parse_item(li: Tag) -> dict[str, Any] | None:
        for span in li.find_all("span", class_="flagicon"):
            span.decompose()

        team_a = li.find("a")
        if not team_a:
            return None

        team_name = team_a.get_text(" ", strip=True)
        if not team_name:
            return None

        record: dict[str, Any] = {"team": team_name}
        if team_a.has_attr("href"):
            record["team_url"] = team_a["href"]

        full_text = li.get_text(" ", strip=True)
        match = re.search(r"\((.+?)\)", full_text)
        if match:
            seasons_raw = clean_wiki_text(match.group(1))
            seasons = parse_seasons(seasons_raw)
            if seasons:
                record["seasons"] = [season.to_dict() for season in seasons]

        return record


class PrivateerTeamsSectionParser(SectionParser):
    def __init__(self, *, list_parser: WikiListHtmlParserABC | None = None) -> None:
        super().__init__()
        self._list_parser = list_parser or PrivateerTeamsListParser()

    def parse(self, element: Tag, *_args: Any, **_kwargs: Any) -> dict[str, Any]:
        if element.name in {"ul", "ol"}:
            return self._list_parser.parse(element)

        list_root = element.find(["ul", "ol"])
        if isinstance(list_root, Tag):
            return self._list_parser.parse(list_root)
        return self.parse_group(list(element.children), *_args, **_kwargs)

    def parse_group(
        self,
        elements: list,
        *_args: Any,
        **_kwargs: Any,
    ) -> dict[str, Any]:
        for candidate in elements:
            if isinstance(candidate, Tag) and candidate.name in {"ul", "ol"}:
                return self._list_parser.parse(candidate)
        return {"items": []}
