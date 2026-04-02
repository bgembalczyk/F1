from __future__ import annotations

import re
from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from infrastructure.http_client.policies.http import HttpPolicy
from models.services.season_service import parse_seasons
from scrapers.base.helpers.http import build_http_policy
from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.list.scraper import F1ListScraper
from scrapers.base.options import ScraperOptions
from scrapers.wiki.parsers.elements.list import ListParser
from scrapers.wiki.parsers.sections.section import SectionParser


class PrivateerTeamsListParser(ListParser):
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
    def __init__(self) -> None:
        super().__init__()
        self._list_parser = PrivateerTeamsListParser()

    def parse(self, element: Tag, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return self.parse_group(list(element.children), *args, **kwargs)

    def parse_group(self, elements: list, *args: Any, **kwargs: Any) -> dict[str, Any]:
        for candidate in elements:
            if isinstance(candidate, Tag) and candidate.name in {"ul", "ol"}:
                return self._list_parser.parse(candidate)
        return {"items": []}


class PrivateerTeamsListScraper(F1ListScraper):
    url = "https://en.wikipedia.org/wiki/List_of_Formula_One_constructors"
    section_id = "Privateer_teams"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._section_parser = PrivateerTeamsSectionParser()

    def get_http_policy(self, options: ScraperOptions) -> HttpPolicy:
        base_policy = super().get_http_policy(options)
        return build_http_policy(
            timeout=max(base_policy.timeout, 20),
            retries=max(base_policy.retries, 2),
            cache=base_policy.cache,
        )

    def _parse_soup(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        root_list = self._find_list_root(soup)
        parsed = self._section_parser.parse(root_list)
        records = parsed.get("items", [])
        if not self.include_urls:
            for record in records:
                record.pop("team_url", None)
            return records

        for record in records:
            url = record.get("team_url")
            if isinstance(url, str):
                record["team_url"] = self._full_url(url)
        return records


if __name__ == "__main__":
    from scrapers.base.deprecated_entrypoint import run_deprecated_entrypoint

    run_deprecated_entrypoint()
