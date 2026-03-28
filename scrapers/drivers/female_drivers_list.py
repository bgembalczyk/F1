from models.records.factories.build import RECORD_BUILDERS
from scrapers.base.table.columns.types import LinksListColumn
from scrapers.base.table.columns.types import PointsColumn
from scrapers.base.table.columns.types import SeasonsColumn
from scrapers.base.table.columns.types import SkipColumn
from scrapers.base.table.columns.types import UrlColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.config import build_scraper_config
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

    CONFIG = build_scraper_config(
        url="https://en.wikipedia.org/wiki/List_of_female_Formula_One_drivers",
        section_id=FEMALE_DRIVERS_SECTION_ID,
        expected_headers=FEMALE_DRIVERS_HEADERS,
        schema=TableSchemaDSL(columns=schema_columns),
        record_factory=RECORD_BUILDERS.special_driver,
    )


if __name__ == "__main__":
    from scrapers.base.deprecated_entrypoint import run_deprecated_entrypoint

    run_deprecated_entrypoint()
