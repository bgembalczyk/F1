from __future__ import annotations

from pathlib import Path

from scrapers.base.registry import register_scraper
from scrapers.base.table.columns.types.enum_marks import EnumMarksColumn
from scrapers.base.table.columns.types.float import FloatColumn
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.multi import MultiColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.scraper import F1TableScraper
from models.engine_manufacturer import EngineManufacturer
from scrapers.base.options import ScraperOptions
from scrapers.base.run import RunConfig, run_and_export


@register_scraper(
    "engine_manufacturers",
    "engines/f1_engine_manufacturers.json",
    "engines/f1_engine_manufacturers.csv",
)
class EngineManufacturersListScraper(F1TableScraper):
    """
    Lista konstruktorów silników F1:
    https://en.wikipedia.org/wiki/List_of_Formula_One_engine_manufacturers#Engine_manufacturers
    """

    CONFIG = ScraperConfig(
        url="https://en.wikipedia.org/wiki/List_of_Formula_One_engine_manufacturers",
        # sekcja z główną tabelą
        section_id="Engine_manufacturers",
        # wystarczy podzbiór nagłówków żeby znaleźć właściwą tabelę
        expected_headers=[
            "Manufacturer",
            "Engines built in",
            "Seasons",
            "Races Entered",
            "Races Started",
            "Wins",
            "Points",
        ],
        model_class=EngineManufacturer,
        column_map={
            "Manufacturer": "manufacturer",
            "Engines built in": "engines_built_in",
            "Seasons": "seasons",
            "Races Entered": "races_entered",
            "Races Started": "races_started",
            "Wins": "wins",
            "Points": "points",
            "Poles": "poles",
            "FL": "fastest_laps",
            "Podiums": "podiums",
            "WCC": "wcc",
            "WDC": "wdc",
        },
        # klucz/nagłówek -> kolumna
        columns={
            # Manufacturer → MultiColumn:
            # - manufacturer: {text, url}
            # - manufacturer_status: enum na podstawie markera
            #
            # Na wiki aktualni konstruktorzy mają w komórce nazwę z "~",
            # np. "Ferrari~" – to mapujemy na "current", reszta na "former".
            "manufacturer": MultiColumn(
                {
                    "manufacturer": UrlColumn(),  # czyści tekst, zwraca dict{text, url}
                    "manufacturer_status": EnumMarksColumn(
                        {"~": "current"},
                        default="former",
                    ),
                }
            ),
            "engines_built_in": LinksListColumn(),
            # sezony jako struktura (np. listy zakresów)
            "seasons": SeasonsColumn(),
            # pola liczbowe
            "races_entered": IntColumn(),
            "races_started": IntColumn(),
            "wins": IntColumn(),
            "points": FloatColumn(),  # ma np. 405.5 itd.
            "poles": IntColumn(),
            "fastest_laps": IntColumn(),
            "podiums": IntColumn(),
            "wcc": IntColumn(),
            "wdc": IntColumn(),
        },
    )


if __name__ == "__main__":
    run_and_export(
        EngineManufacturersListScraper,
        "engines/f1_engine_manufacturers.json",
        "engines/f1_engine_manufacturers.csv",
        run_config=RunConfig(
            include_urls=True,
            output_dir=Path("../../data/wiki"),
            options=ScraperOptions(include_urls=True),
        ),
    )
