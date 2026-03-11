from pathlib import Path

from models.validation.engine_manufacturer import EngineManufacturer
from scrapers.base.helpers.runner import run_and_export
from scrapers.base.run_config import RunConfig
from scrapers.base.table.columns.types.float import FloatColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.dsl import TableSchemaDSL
from scrapers.base.table.dsl import column
from scrapers.base.table.presets import BASE_STATS_COLUMNS
from scrapers.base.table.presets import BASE_STATS_MAP
from scrapers.base.table.scraper import F1TableScraper
from scrapers.engines.columns.manufacturer_name_status import (
    EngineManufacturerNameStatusColumn,
)


class EngineManufacturersListScraper(F1TableScraper):
    """
    Lista konstruktorów silników F1:
    https://en.wikipedia.org/wiki/List_of_Formula_One_engine_manufacturers#Engine_manufacturers
    """

    schema_columns = [
        column("Manufacturer", "manufacturer", EngineManufacturerNameStatusColumn()),
        column("Engines built in", "engines_built_in", LinksListColumn()),
    ]
    for header, key in BASE_STATS_MAP.items():
        column_instance = FloatColumn() if key == "points" else BASE_STATS_COLUMNS[key]
        schema_columns.append(column(header, key, column_instance))

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
        record_factory=EngineManufacturer,
        schema=TableSchemaDSL(columns=schema_columns),
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
