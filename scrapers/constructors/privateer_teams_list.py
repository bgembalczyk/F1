import re
from pathlib import Path
from typing import Any

from bs4 import Tag

from infrastructure.http_client.policies.http import HttpPolicy
from models.services.season_service import parse_seasons
from scrapers.base.helpers.http import build_http_policy
from scrapers.base.helpers.runner import run_and_export
from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.list.scraper import F1ListScraper
from scrapers.base.options import ScraperOptions
from scrapers.base.run_config import RunConfig


class PrivateerTeamsListScraper(F1ListScraper):
    """
    Lista privateer teams (sekcja 'Privateer teams').

    Każdy element listy ma strukturę:
        [flagi kraju] <a>NAZWA ZESPOŁU</a> (lata aktywności)

    Flagi ignorujemy całkowicie, zapisujemy:
        - team       - tekst linka z nazwą zespołu,
        - team_url   - pełny URL do strony zespołu (opcjonalnie),
        - seasons    - lista słowników {"year": YYYY, "url": "..."}.
    """

    url = "https://en.wikipedia.org/wiki/List_of_Formula_One_constructors"
    section_id = "Privateer_teams"

    def get_http_policy(self, options: ScraperOptions) -> HttpPolicy:
        base_policy = super().get_http_policy(options)
        return build_http_policy(
            timeout=max(base_policy.timeout, 20),
            retries=max(base_policy.retries, 2),
            cache=base_policy.cache,
        )

    def parse_item(self, li: Tag) -> dict[str, Any] | None:
        # 1) wywalamy wszystkie flagi, żeby nie przeszkadzały w szukaniu linka zespołu
        for span in li.find_all("span", class_="flagicon"):
            span.decompose()

        # 2) link z nazwą zespołu = pierwszy <a> po usunięciu flag
        team_a = li.find("a")
        if not team_a:
            return None

        team_name = team_a.get_text(" ", strip=True)
        if not team_name:
            return None

        record: dict[str, Any] = {"team": team_name}

        # 3) URL zespołu (opcjonalnie)
        if self.include_urls and team_a.has_attr("href"):
            record["team_url"] = self._full_url(team_a["href"])

        # 4) wyciągamy tekst z nawiasu i zamieniamy na seasons
        full_text = li.get_text(" ", strip=True)
        # np. "BMS Scuderia Italia (1988-1993)"
        m = re.search(r"\((.+?)\)", full_text)
        if m:
            seasons_raw = clean_wiki_text(m.group(1))
            seasons = parse_seasons(seasons_raw)
            if seasons:
                record["seasons"] = seasons

        return record


if __name__ == "__main__":
    run_and_export(
        PrivateerTeamsListScraper,
        "constructors/f1_privateer_teams.json",
        "constructors/f1_privateer_teams.csv",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
            debug_dir=Path("../../data/debug"),
        ),
    )
