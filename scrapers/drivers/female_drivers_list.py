from pathlib import Path

from scrapers.base.helpers.runner import run_and_export
from scrapers.base.run_config import RunConfig
from models.records.factories import build_special_driver_record
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.points import PointsColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.skip import SkipColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.dsl import TableSchemaDSL, column
from scrapers.base.table.scraper import F1TableScraper
from scrapers.base.options import ScraperOptions
from scrapers.drivers.columns.entries_starts import EntriesStartsColumn
from scrapers.drivers.constants import (
    FEMALE_DRIVER_ENTRIES_STARTS_HEADER,
    FEMALE_DRIVER_NAME_HEADER,
    FEMALE_DRIVER_POINTS_HEADER,
    FEMALE_DRIVER_SEASONS_HEADER,
    FEMALE_DRIVER_TEAMS_HEADER,
    FEMALE_DRIVERS_HEADERS,
    FEMALE_DRIVERS_INDEX_HEADER,
    FEMALE_DRIVERS_SECTION_ID,
)
from scrapers.drivers.post_processors import EntriesStartsPointsPostProcessor


class FemaleDriversListScraper(F1TableScraper):
    """
    Scraper listy oficjalnych kobiet-kierowców F1 z:
    https://en.wikipedia.org/wiki/List_of_female_Formula_One_drivers
    """

    schema_columns = [
        column(FEMALE_DRIVERS_INDEX_HEADER, "_skip", SkipColumn()),
        column(FEMALE_DRIVER_NAME_HEADER, "driver", UrlColumn()),
        column(FEMALE_DRIVER_SEASONS_HEADER, "seasons", SeasonsColumn()),
        column(FEMALE_DRIVER_TEAMS_HEADER, "teams", LinksListColumn()),
        column(
            FEMALE_DRIVER_ENTRIES_STARTS_HEADER,
            "entries_starts",
            EntriesStartsColumn(),
        ),
        column(FEMALE_DRIVER_POINTS_HEADER, "points", PointsColumn()),
    ]

    CONFIG = ScraperConfig(
        url="https://en.wikipedia.org/wiki/List_of_female_Formula_One_drivers",
        section_id=FEMALE_DRIVERS_SECTION_ID,
        expected_headers=FEMALE_DRIVERS_HEADERS,
        schema=TableSchemaDSL(columns=schema_columns),
        record_factory=build_special_driver_record,
    )

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        config: ScraperConfig | None = None,
    ) -> None:
        resolved_options = options or ScraperOptions()
        if not any(
            isinstance(post_processor, EntriesStartsPointsPostProcessor)
            for post_processor in resolved_options.post_processors or []
        ):
            resolved_options.post_processors.append(EntriesStartsPointsPostProcessor())
        super().__init__(options=resolved_options, config=config)


if __name__ == "__main__":
    run_and_export(
        FemaleDriversListScraper,
        "drivers/female_drivers.json",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
            debug_dir=Path("../../data/debug"),
        ),
    )
