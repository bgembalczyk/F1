"""DEPRECATED ENTRYPOINT: use scrapers.grands_prix.entrypoint.run_list_scraper."""

from models.records.factories.build import build_grands_prix_record
from scrapers.base.options import ScraperOptions
from scrapers.base.table.builders import build_columns
from scrapers.base.table.builders import build_scraper_config
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.dsl.column import column
from scrapers.base.table.scraper import F1TableScraper
from scrapers.grands_prix.columns.race_title_status import RaceTitleStatusColumn
from scrapers.grands_prix.validator import GrandsPrixRecordValidator
from scrapers.wiki.component_metadata import ComponentMetadata


class GrandsPrixListScraper(F1TableScraper):
    COMPONENT_METADATA = ComponentMetadata.build_layer_one_list_scraper(
        domain="grands_prix",
        default_output_path="raw/grands_prix/seeds/f1_grands_prix_extended.json",
        legacy_output_path="grands_prix/f1_grands_prix_extended.json",
    )

    """
    Uproszczony scraper np. dla tabeli 'By race title'
    z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_Grands_Prix
    """

    default_validator = GrandsPrixRecordValidator()
    options_domain = "grands_prix"
    options_profile = "soft_seed"

    schema_columns = build_columns(
        column("Race title", "race_title", RaceTitleStatusColumn()),
        column("Country", "country", LinksListColumn()),
        column("Years held", "years_held", SeasonsColumn()),
        column("Circuits", "circuits", IntColumn()),
        column("Total", "total", IntColumn()),
    )

    CONFIG = build_scraper_config(
        url="https://en.wikipedia.org/wiki/List_of_Formula_One_Grands_Prix",
        section_id="By_race_title",
        # podzbiór nagłówków - do znalezienia właściwej tabeli
        expected_headers=[
            "Race title",
            "Years held",
        ],
        columns=schema_columns,
        record_factory=build_grands_prix_record,
    )

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        config=None,
    ) -> None:
        super().__init__(options=options, config=config)


if __name__ == "__main__":
    from scrapers.cli import run_legacy_wrapper

    run_legacy_wrapper("scrapers.grands_prix.list_scraper")
