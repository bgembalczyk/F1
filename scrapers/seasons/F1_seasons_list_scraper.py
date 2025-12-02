from __future__ import annotations

from typing import Dict

from scrapers.F1_table_scraper import F1TableScraper
from scrapers.helpers.columns.columns import UrlColumn, LinksListColumn, IntColumn


class F1SeasonsListScraper(F1TableScraper):
    """
    Scraper listy sezonów z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_seasons
    (główna tabela World Championship seasons)
    """

    url = "https://en.wikipedia.org/wiki/List_of_Formula_One_seasons"
    # jeśli id sekcji się kiedyś zmieni – poprawiasz tylko to
    section_id = "Seasons"

    # nagłówki, które MUSZĄ wystąpić w tabeli
    expected_headers = [
        "Season",
        "Races",
    ]

    # mapowanie: nagłówek z tabeli -> klucz w dict wynikowym
    column_map: Dict[str, str] = {
        "Season": "season",
        "Races": "races",
        "Countries": "countries",
        "First": "first",
        "Last": "last",
        "Drivers' Champion (team)": "drivers_champion_team",
        "Constructors' Champion": "constructors_champion",
        "Winners": "winners",
    }

    # logika kolumn po stronie KLUCZA (po column_map)
    columns = {
        # Season → pojedynczy link {text, url} z automatycznym czyszczeniem * † itd.
        "season": UrlColumn(),
        # Races → int
        "races": IntColumn(),
        "countries": IntColumn(),
        "first": UrlColumn(),
        "last": UrlColumn(),
        # Mistrzowie → zawsze lista linków [{text, url}, ...]
        "drivers_champion_team": LinksListColumn(),
        "constructors_champion": LinksListColumn(),
        "winners": IntColumn(),
    }


if __name__ == "__main__":
    scraper = F1SeasonsListScraper(include_urls=True)

    seasons = scraper.fetch()
    print(f"Pobrano rekordów: {len(seasons)}")

    scraper.to_json("../../data/wiki/seasons/f1_seasons.json")
    scraper.to_csv("../../data/wiki/seasons/f1_seasons.csv")
