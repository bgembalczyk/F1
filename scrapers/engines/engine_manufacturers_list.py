from models.records.factories.build import RECORD_BUILDERS
from models.validation.engine_manufacturer import EngineManufacturer
from scrapers.base.source_catalog import ENGINES_LIST
from scrapers.base.table.builders import build_base_stats_columns
from scrapers.base.table.builders import build_columns
from scrapers.base.table.builders import build_entity_metadata_columns
from scrapers.base.table.builders import build_name_status_fragment
from scrapers.base.table.builders import entity_column
from scrapers.base.table.builders import build_scraper_config
from scrapers.base.table.config import build_scraper_config
from scrapers.base.table.columns.types import FloatColumn
from scrapers.base.table.columns.types import LinksListColumn
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
        build_name_status_fragment(
            header="Manufacturer",
            output_key="manufacturer",
            column_type=EngineManufacturerNameStatusColumn(),
        ),
        build_entity_metadata_columns(
            [
                entity_column("Engines built in", "engines_built_in", LinksListColumn()),
            ],
        ),
        build_base_stats_columns(column_overrides={"points": FloatColumn()}),
    )

    CONFIG = build_scraper_config(
        url=ENGINES_LIST.base_url,
        # sekcja z główną tabelą
        section_id=ENGINES_LIST.section_id,
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
        record_factory=RECORD_BUILDERS.engine_manufacturer,
        model_class=EngineManufacturer,
        columns=schema_columns,
    )


if __name__ == "__main__":
    from scrapers.base.deprecated_entrypoint import run_deprecated_entrypoint

    run_deprecated_entrypoint()
