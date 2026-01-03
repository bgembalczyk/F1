from pathlib import Path

from scrapers.base.helpers.runner import run_and_export
from scrapers.base.run_config import RunConfig
from models.records.factories import build_season_record
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.scraper import F1TableScraper


class SeasonsListScraper(F1TableScraper):
    """
    Scraper listy sezonów z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_seasons
    (główna tabela World Championship seasons)
    """

    CONFIG = ScraperConfig(
        url="https://en.wikipedia.org/wiki/List_of_Formula_One_seasons",
        # jeśli id sekcji się kiedyś zmieni – poprawiasz tylko to
        section_id="Seasons",
        # nagłówki, które MUSZĄ wystąpić w tabeli
        expected_headers=[
            "Season",
            "Races",
        ],
        # mapowanie: nagłówek z tabeli -> klucz w dict wynikowym
        column_map={
            "Season": "season",
            "Races": "races",
            "Countries": "countries",
            "First": "first",
            "Last": "last",
            "Drivers' Champion (team)": "drivers_champion_team",
            "Constructors' Champion": "constructors_champion",
            "Winners": "winners",
        },
        # logika kolumn po stronie KLUCZA (po column_map)
        columns={
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
        },
        record_factory=build_season_record,
    )


if __name__ == "__main__":
    run_and_export(
        SeasonsListScraper,
        "seasons/f1_seasons.json",
        "seasons/f1_seasons.csv",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
        ),
    )
