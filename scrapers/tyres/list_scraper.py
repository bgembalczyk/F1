from scrapers.base.factory.record_factory import RECORD_FACTORIES
from scrapers.base.source_catalog import TYRES
from scrapers.base.table.columns.types import SeasonsColumn
from scrapers.base.table.columns.types import SkipColumn
from scrapers.base.table.config import build_scraper_config
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.base.table.scraper import F1TableScraper
from scrapers.seasons.columns.seasons import SeasonsColumn
from scrapers.tyres.columns.append_links import AppendLinksColumn


class TyreManufacturersBySeasonScraper(F1TableScraper):
    """
    Scraper producentów opon F1:
    https://en.wikipedia.org/wiki/Formula_One_tyres#Tyre_manufacturers_by_season
    """

    schema_columns = [
        column("Season", "seasons", SeasonsColumn()),
        column("Manufacturer 1", "manufacturers", AppendLinksColumn()),
        column("Manufacturer 2", "manufacturers", AppendLinksColumn()),
        column("Manufacturer 3", "manufacturers", AppendLinksColumn()),
        column("Manufacturer 4", "manufacturers", AppendLinksColumn()),
        column("Manufacturer 5", "manufacturers", AppendLinksColumn()),
        column("Manufacturer 6", "manufacturers", AppendLinksColumn()),
        column("Wins", "wins", SkipColumn()),
    ]

    CONFIG = build_scraper_config(
        url=TYRES.url(),
        section_id=TYRES.section_id,
        expected_headers=[
            "Season",
            "Manufacturer 1",
            "Wins",
        ],
        schema=TableSchemaDSL(columns=schema_columns),
        record_factory=RECORD_FACTORIES.mapping(),
    )


if __name__ == "__main__":
    from scrapers.base.deprecated_entrypoint import run_deprecated_entrypoint

    run_deprecated_entrypoint()
