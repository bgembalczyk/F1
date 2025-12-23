from pathlib import Path

from models.validation.engine_manufacturer import EngineManufacturer
from scrapers.base.runner import RunConfig, run_and_export
from scrapers.base.table.columns.types.enum_marks import EnumMarksColumn
from scrapers.base.table.columns.types.float import FloatColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.multi import MultiColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.presets import BASE_STATS_COLUMNS, BASE_STATS_MAP
from scrapers.base.table.scraper import F1TableScraper


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
            **BASE_STATS_MAP,
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
            **BASE_STATS_COLUMNS,
            "points": FloatColumn(),  # ma np. 405.5 itd.
        },
    )


if __name__ == "__main__":
    run_and_export(
        EngineManufacturersListScraper,
        "engines/f1_engine_manufacturers.json",
        "engines/f1_engine_manufacturers.csv",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
        ),
    )
