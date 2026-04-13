import re
from typing import Any

from bs4 import Tag

from models.services.season import parse_seasons
from scrapers.helpers.text import clean_wiki_text
from scrapers.parsers.contracts.wiki_elements import WikiListElementParserABC


class PrivateerTeamsListParser(WikiListElementParserABC):
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
