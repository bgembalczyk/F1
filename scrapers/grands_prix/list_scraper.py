"""DEPRECATED ENTRYPOINT: use scrapers.grands_prix.entrypoint.run_list_scraper."""

from models.records.factories.build import RECORD_BUILDERS
from scrapers.base.table.builders import build_columns
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.dsl.column import column
from scrapers.base.table.config import build_scraper_config
from scrapers.base.table.seed_list_scraper import SeedListTableScraper
from scrapers.grands_prix.columns.race_title_status import RaceTitleStatusColumn
from scrapers.grands_prix.validator import GrandsPrixRecordValidator


class GrandsPrixListScraper(SeedListTableScraper):
    domain = "grands_prix"
    default_output_path = "raw/grands_prix/seeds/f1_grands_prix_extended.json"
    legacy_output_path = "grands_prix/f1_grands_prix_extended.json"

    """
    Uproszczony scraper np. dla tabeli 'By race title'
    z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_Grands_Prix
    """

    default_validator = GrandsPrixRecordValidator()

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
        record_factory=RECORD_BUILDERS.grands_prix,
    )


if __name__ == "__main__":
    from scrapers.cli import run_current_legacy_wrapper

    run_current_legacy_wrapper()
