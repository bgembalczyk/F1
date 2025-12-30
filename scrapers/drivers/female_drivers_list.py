from pathlib import Path
import re
from typing import Optional, Tuple

from scrapers.base.runner import RunConfig, run_and_export
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.func import FuncColumn
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.multi import MultiColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.scraper import F1TableScraper


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
            "Name": "driver",
            "Seasons": "seasons",
            "Teams": "teams",
            "Entries (starts)": "entries_starts",
            "Points": "points",
        },
        columns={
            "driver": UrlColumn(),
            "seasons": SeasonsColumn(),
            "teams": LinksListColumn(),
            "entries_starts": MultiColumn(
                {
                    "entries": FuncColumn(lambda ctx: _parse_entries_starts(ctx)[0]),
                    "starts": FuncColumn(lambda ctx: _parse_entries_starts(ctx)[1]),
                }
            ),
            "points": IntColumn(),
        },
    )


def _parse_entries_starts(ctx: ColumnContext) -> Tuple[Optional[int], Optional[int]]:
    text = (ctx.clean_text or ctx.raw_text or "").strip()
    if not text:
        return None, None

    values = [int(value) for value in re.findall(r"\d+", text)]
    if not values:
        return None, None

    entries = values[0]
    starts = values[1] if len(values) > 1 else None
    return entries, starts


if __name__ == "__main__":
    run_and_export(
        FemaleDriversListScraper,
        "drivers/female_drivers.json",
        "drivers/female_drivers.csv",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
        ),
    )
