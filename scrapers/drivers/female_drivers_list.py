from pathlib import Path

from scrapers.base.helpers.runner import run_and_export
from scrapers.base.run_config import RunConfig
from scrapers.base.records import record_from_mapping
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.points import PointsColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.skip import SkipColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.dsl import TableSchemaDSL, column
from scrapers.base.table.scraper import F1TableScraper
from scrapers.drivers.columns.entries_starts import EntriesStartsColumn
from scrapers.drivers.constants import (
    FEMALE_DRIVER_ENTRIES_STARTS_HEADER,
    FEMALE_DRIVER_NAME_HEADER,
    FEMALE_DRIVER_POINTS_HEADER,
    FEMALE_DRIVER_SEASONS_HEADER,
    FEMALE_DRIVER_TEAMS_HEADER,
    FEMALE_DRIVERS_HEADERS,
    FEMALE_DRIVERS_SECTION_ID,
    INDEX_HEADER,
)


class FemaleDriversListScraper(F1TableScraper):
    """
    Scraper listy oficjalnych kobiet-kierowców F1 z:
    https://en.wikipedia.org/wiki/List_of_female_Formula_One_drivers
    """

    schema_columns = [
        column(INDEX_HEADER, "_skip", SkipColumn()),
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
        record_factory=record_from_mapping,
    )

    def _parse_soup(self, soup):
        records = super()._parse_soup(soup)
        for record in records:
            entries = record.get("entries")
            starts = record.get("starts")
            points = record.get("points")
            if (
                entries == 0
                and starts is not None
                and starts > 0
                and points is not None
            ):
                record["entries"] = starts
                record["starts"] = None
                record["points"] = None
        return records


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
