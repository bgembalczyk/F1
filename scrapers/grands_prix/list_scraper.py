"""DEPRECATED ENTRYPOINT: use scrapers.grands_prix.entrypoint.run_list_scraper."""

from models.records.factories.build import RECORD_BUILDERS
from scrapers.base.source_catalog import GRANDS_PRIX_LIST
from scrapers.base.factory.record_factory import RECORD_FACTORIES
from scrapers.base.table.builders import build_columns
from scrapers.base.table.builders import build_entity_metadata_columns
from scrapers.base.table.builders import build_name_status_fragment
from scrapers.base.table.builders import entity_column
from scrapers.base.table.columns.types import IntColumn
from scrapers.base.table.columns.types import LinksListColumn
from scrapers.base.table.columns.types import SeasonsColumn
from scrapers.base.table.config import build_scraper_config
from scrapers.base.table.seed_list_scraper import SeedListTableScraper
from scrapers.grands_prix.columns.race_title_status import RaceTitleStatusColumn


class GrandsPrixListScraper(SeedListTableScraper):
    domain = "grands_prix"
    output_basename = "f1_grands_prix_extended.json"

    """
    Uproszczony scraper np. dla tabeli 'By race title'
    z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_Grands_Prix
    """

    schema_columns = build_columns(
        build_name_status_fragment(
            header="Race title",
            output_key="race_title",
            column_type=RaceTitleStatusColumn(),
        ),
        build_entity_metadata_columns(
            [
                entity_column("Country", "country", LinksListColumn()),
                entity_column("Years held", "years_held", SeasonsColumn()),
                entity_column("Circuits", "circuits", IntColumn()),
                entity_column("Total", "total", IntColumn()),
            ],
        ),
    )

    CONFIG = build_scraper_config(
        url=GRANDS_PRIX_LIST.base_url,
        section_id=GRANDS_PRIX_LIST.section_id,
        # podzbiór nagłówków - do znalezienia właściwej tabeli
        expected_headers=[
            "Race title",
            "Years held",
        ],
        columns=schema_columns,
        record_factory=RECORD_FACTORIES.builders("grands_prix"),
    )


if __name__ == "__main__":
    from scrapers.base.deprecated_entrypoint import run_deprecated_entrypoint

    run_deprecated_entrypoint()
