from typing import Dict, Any, Optional
import re

from bs4 import Tag

from scrapers.base.list.scrapper import F1ListScraper
from scrapers.base.table.helpers.utils import clean_wiki_text, parse_seasons


class F1PrivateerTeamsListScraper(F1ListScraper):
    """
    Lista privateer teams (sekcja 'Privateer teams').

    Każdy element listy ma strukturę:
        [flagi kraju] <a>NAZWA ZESPOŁU</a> (lata aktywności)

    Flagi ignorujemy całkowicie, zapisujemy:
        - team       – tekst linka z nazwą zespołu,
        - team_url   – pełny URL do strony zespołu (opcjonalnie),
        - seasons    – lista słowników {"year": YYYY, "url": "..."}.
    """

    url = "https://en.wikipedia.org/wiki/List_of_Formula_One_constructors"

    data_resource = "constructors"
    data_file_stem = "f1_privateer_teams"
    section_id = "Privateer_teams"

    def parse_item(self, li: Tag) -> Optional[Dict[str, Any]]:
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

        record: Dict[str, Any] = {"team": team_name}

        # 3) URL zespołu (opcjonalnie)
        if self.include_urls and team_a.has_attr("href"):
            record["team_url"] = self._full_url(team_a["href"])

        # 4) wyciągamy tekst z nawiasu i zamieniamy na seasons
        full_text = li.get_text(" ", strip=True)
        # np. "BMS Scuderia Italia (1988–1993)"
        m = re.search(r"\((.+?)\)", full_text)
        if m:
            seasons_raw = clean_wiki_text(m.group(1))
            seasons = parse_seasons(seasons_raw)
            if seasons:
                record["seasons"] = seasons

        return record
