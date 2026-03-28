from models.records.factories.build import RECORD_BUILDERS
from models.validation.engine_manufacturer import EngineManufacturer
from scrapers.base.table.builders import build_base_stats_columns
from scrapers.base.table.builders import build_columns
from scrapers.base.table.columns.types.float import FloatColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.dsl.column import column
from scrapers.base.table.seed_list_scraper import BaseSeedListScraper
from scrapers.engines.columns.manufacturer_name_status import (
    EngineManufacturerNameStatusColumn,
)


class EngineManufacturersListScraper(BaseSeedListScraper):
    domain = "engines"
    default_output_path = "raw/engines/seeds/engine_manufacturers"
    legacy_output_path = "engines/engine_manufacturers"

    """
    Lista konstruktorów silników F1:
    https://en.wikipedia.org/wiki/List_of_Formula_One_engine_manufacturers#Engine_manufacturers
    """

    schema_columns = build_columns(
        column("Manufacturer", "manufacturer", EngineManufacturerNameStatusColumn()),
        column("Engines built in", "engines_built_in", LinksListColumn()),
        build_base_stats_columns(column_overrides={"points": FloatColumn()}),
    )

    CONFIG = BaseSeedListScraper.build_config(
        url="https://en.wikipedia.org/wiki/List_of_Formula_One_engine_manufacturers",
        section_id="Engine_manufacturers",
        expected_headers=[
            "Manufacturer",
            "Engines built in",
            "Seasons",
            "Races Entered",
            "Races Started",
            "Wins",
            "Points",
        ],
        record_factory=RECORD_BUILDERS.engine_manufacturer,
        model_class=EngineManufacturer,
        columns=schema_columns,
    )


if __name__ == "__main__":
    from scrapers.cli import run_current_legacy_wrapper

    run_current_legacy_wrapper()
