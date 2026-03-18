from models.records.factories.build import build_engine_manufacturer_record
from models.validation.engine_manufacturer import EngineManufacturer
from scrapers.base.table.builders import build_base_stats_columns
from scrapers.base.table.builders import build_columns
from scrapers.base.table.builders import build_scraper_config
from scrapers.base.table.columns.types.float import FloatColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.dsl.column import column
from scrapers.base.table.scraper import F1TableScraper
from scrapers.engines.columns.manufacturer_name_status import (
    EngineManufacturerNameStatusColumn,
)


class EngineManufacturersListScraper(F1TableScraper):
    """
    Lista konstruktorów silników F1:
    https://en.wikipedia.org/wiki/List_of_Formula_One_engine_manufacturers#Engine_manufacturers
    """

    schema_columns = build_columns(
        column("Manufacturer", "manufacturer", EngineManufacturerNameStatusColumn()),
        column("Engines built in", "engines_built_in", LinksListColumn()),
        build_base_stats_columns(column_overrides={"points": FloatColumn()}),
    )

    CONFIG = build_scraper_config(
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
        record_factory=build_engine_manufacturer_record,
        model_class=EngineManufacturer,
        columns=schema_columns,
    )


if __name__ == "__main__":
    from scrapers.cli import run_current_legacy_wrapper

    run_current_legacy_wrapper()
