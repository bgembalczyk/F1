from __future__ import annotations

from typing import Dict

from scrapers.base.table.columns.types.enum_marks import EnumMarksColumn
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.multi import MultiColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.scraper import F1TableScraper


class F1GrandsPrixListScraper(F1TableScraper):
    """
    Uproszczony scraper np. dla tabeli 'By race title'
    z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_Grands_Prix
    """

    url = "https://en.wikipedia.org/wiki/List_of_Formula_One_Grands_Prix"
    section_id = "By_race_title"

    # podzbiór nagłówków – do znalezienia właściwej tabeli
    expected_headers = [
        "Race title",
        "Years held",
    ]

    # mapowanie nagłówek -> klucz w dict
    column_map: Dict[str, str] = {
        "Race title": "race_title",
        "Country": "country",
        "Years held": "years_held",
        "Circuits": "circuits",
        "Total": "total",
    }

    # klucz/nagłówek -> kolumna
    #
    # - race_title: MultiColumn → { race_title (link), race_status (enum po znaku *) }
    # - years_held: sezony
    # - races_held: int
    # - country: lista linków [{text, url}, ...]
    columns = {
        # Race title → MultiColumn:
        #   - race_title: pierwszy link (UrlColumn) z automatycznym czyszczeniem * / † z .text
        #   - race_status: EnumMarksColumn patrzący na raw_text (gwiazdka = aktywne)
        "race_title": MultiColumn(
            {
                "race_title": UrlColumn(),
                "race_status": EnumMarksColumn(
                    {"*": "active"},
                    default="past",
                ),
            }
        ),
        # Country → lista linków [{text, url}, ...] z czyszczeniem znaczników
        "country": LinksListColumn(),
        # Years held → sezony (lista zakresów/lat)
        "years_held": SeasonsColumn(),
        "circuits": IntColumn(),
        "total": IntColumn(),
    }


if __name__ == "__main__":
    scraper = F1GrandsPrixListScraper(include_urls=True)

    races = scraper.fetch()
    print(f"Pobrano rekordów: {len(races)}")

    scraper.to_json("../../data/wiki/grands_prix/f1_grands_prix_by_title.json")
    scraper.to_csv("../../data/wiki/grands_prix/f1_grands_prix_by_title.csv")
