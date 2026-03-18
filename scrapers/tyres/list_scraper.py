from scrapers.base.records import record_from_mapping
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.skip import SkipColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.base.table.scraper import F1TableScraper
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

    CONFIG = ScraperConfig(
        url="https://en.wikipedia.org/wiki/Formula_One_tyres#Tyre_manufacturers_by_season",
        section_id="Tyre_manufacturers_by_season",
        expected_headers=[
            "Season",
            "Manufacturer 1",
            "Wins",
        ],
        schema=TableSchemaDSL(columns=schema_columns),
        record_factory=record_from_mapping,
    )


if __name__ == "__main__":
    from scrapers.cli import run_current_legacy_wrapper

    run_current_legacy_wrapper()
