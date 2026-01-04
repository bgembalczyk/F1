from pathlib import Path

from scrapers.base.helpers.config_factory import (
    ScraperCommonConfig,
    build_table_config,
)
from scrapers.base.helpers.runner import run_and_export
from scrapers.base.options import ScraperOptions
from models.records.factories import build_grands_prix_record
from scrapers.base.runner import RunConfig
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.dsl import TableSchemaDSL, column
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
        # podzbiór nagłówków – do znalezienia właściwej tabeli
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
        options = build_table_config(
            options,
            config=ScraperCommonConfig(
                include_urls=True,
                normalize_empty_values=True,
                validation_mode="soft",
            ),
        )
        super().__init__(options=options, config=config)


if __name__ == "__main__":
    run_and_export(
        GrandsPrixListScraper,
        "grands_prix/f1_grands_prix_by_title.json",
        "grands_prix/f1_grands_prix_by_title.csv",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
        ),
    )
