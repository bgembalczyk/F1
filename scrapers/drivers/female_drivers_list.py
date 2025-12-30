from pathlib import Path

from scrapers.base.runner import RunConfig, run_and_export
from scrapers.base.table.columns.types.func import FuncColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.multi import MultiColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.scraper import F1TableScraper
from scrapers.drivers.helpers.parsers import parse_entries_starts
from scrapers.drivers.helpers.parsers import parse_points_from_cell


class FemaleDriversListScraper(F1TableScraper):
    """
    Scraper listy oficjalnych kobiet-kierowców F1 z:
    https://en.wikipedia.org/wiki/List_of_female_Formula_One_drivers
    """

    CONFIG = ScraperConfig(
        url="https://en.wikipedia.org/wiki/List_of_female_Formula_One_drivers",
        section_id="Official_drivers",
        expected_headers=[
            "Name",
            "Seasons",
            "Teams",
            "Entries (starts)",
            "Points",
        ],
        column_map={
            "#": "_skip",
            "Name": "driver",
            "Seasons": "seasons",
            "Teams": "teams",
            "Entries (starts)": "entries_starts",
            "Points": "points",
        },
        columns={
            "_skip": FuncColumn(lambda ctx: ctx.skip_sentinel),
            "driver": UrlColumn(),
            "seasons": SeasonsColumn(),
            "teams": LinksListColumn(),
            "entries_starts": MultiColumn(
                {
                    "entries": FuncColumn(lambda ctx: parse_entries_starts(ctx)[0]),
                    "starts": FuncColumn(lambda ctx: parse_entries_starts(ctx)[1]),
                }
            ),
            "points": FuncColumn(parse_points_from_cell),
        },
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
        ),
    )
