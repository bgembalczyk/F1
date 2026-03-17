"""DEPRECATED ENTRYPOINT: use scrapers.grands_prix.entrypoint.run_list_scraper."""

from models.records.factories import build_grands_prix_record
from scrapers.base.options import ScraperOptions
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.base.table.scraper import F1TableScraper
from scrapers.grands_prix.columns.race_title_status import RaceTitleStatusColumn
from scrapers.grands_prix.validator import GrandsPrixRecordValidator


class GrandsPrixListScraper(F1TableScraper):
    """
    Uproszczony scraper np. dla tabeli 'By race title'
    z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_Grands_Prix
    """

    default_validator = GrandsPrixRecordValidator()
    options_domain = "grands_prix"
    options_profile = "soft_seed"

    schema_columns = [
        column("Race title", "race_title", RaceTitleStatusColumn()),
        column("Country", "country", LinksListColumn()),
        column("Years held", "years_held", SeasonsColumn()),
        column("Circuits", "circuits", IntColumn()),
        column("Total", "total", IntColumn()),
    ]

    CONFIG = ScraperConfig(
        url="https://en.wikipedia.org/wiki/List_of_Formula_One_Grands_Prix",
        section_id="By_race_title",
        # podzbiór nagłówków - do znalezienia właściwej tabeli
        expected_headers=[
            "Race title",
            "Years held",
        ],
        schema=TableSchemaDSL(columns=schema_columns),
        record_factory=build_grands_prix_record,
    )

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        config: ScraperConfig | None = None,
    ) -> None:
        super().__init__(options=options, config=config)


if __name__ == "__main__":
    from scrapers.base.cli_entrypoint import build_deprecated_module_main
    from scrapers.grands_prix.entrypoint import run_list_scraper

    build_deprecated_module_main(
        target=run_list_scraper,
        deprecation_message=(
            "scrapers.grands_prix.list_scraper is deprecated; use "
            "scrapers.grands_prix.entrypoint.run_list_scraper."
        ),
    )()
