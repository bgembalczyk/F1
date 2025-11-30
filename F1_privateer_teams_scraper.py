import json
import csv
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional

from bs4 import BeautifulSoup, Tag

from F1_list_scrapper import F1ListScraper

try:
    import pandas as pd
    _HAS_PANDAS = True
except ImportError:
    _HAS_PANDAS = False


class F1PrivateerTeamsScraper(F1ListScraper):
    """
    Lista privateer teams (sekcja 'Privateer teams').
    """

    url = "https://en.wikipedia.org/wiki/List_of_Formula_One_constructors"
    section_id = "Privateer_teams"

    def parse_item(self, li: Tag) -> Optional[Dict[str, Any]]:
        a = li.find("a")
        text = li.get_text(" ", strip=True)
        if not text:
            return None
        record: Dict[str, Any] = {"team": text}
        if self.include_urls and a and a.has_attr("href"):
            record["team_url"] = self._full_url(a["href"])
        return record


if __name__ == "__main__":
    scraper = F1PrivateerTeamsScraper(include_urls=True)

    teams = scraper.fetch()
    print(f"Pobrano rekordów: {len(teams)}")

    scraper.to_json("f1_privateer_teams.json")
    scraper.to_csv("f1_privateer_teams.csv")

    # opcjonalnie:
    # for t in teams[:5]:
    #     print(t)
    # df = scraper.to_dataframe()
    # print(df.head())
