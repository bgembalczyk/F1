from pathlib import Path

from models.records.factories import build_special_driver_record
from scrapers.base.options import ScraperOptions
from scrapers.base.run_config import RunConfig
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.points import PointsColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.skip import SkipColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.base.table.scraper import F1TableScraper
from scrapers.drivers.columns.entries_starts import EntriesStartsColumn
from scrapers.drivers.constants import FEMALE_DRIVER_ENTRIES_STARTS_HEADER
from scrapers.drivers.constants import FEMALE_DRIVER_NAME_HEADER
from scrapers.drivers.constants import FEMALE_DRIVER_POINTS_HEADER
from scrapers.drivers.constants import FEMALE_DRIVER_SEASONS_HEADER
from scrapers.drivers.constants import FEMALE_DRIVER_TEAMS_HEADER
from scrapers.drivers.constants import FEMALE_DRIVERS_HEADERS
from scrapers.drivers.constants import FEMALE_DRIVERS_INDEX_HEADER
from scrapers.drivers.constants import FEMALE_DRIVERS_SECTION_ID
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
    from scrapers.cli import run_legacy_wrapper

    run_legacy_wrapper("scrapers.drivers.female_drivers_list")
