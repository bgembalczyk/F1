from pathlib import Path
from typing import Any, Dict

from scrapers.base.runner import RunConfig, run_and_export
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.skip import SkipColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.scraper import F1TableScraper


class AppendLinksColumn(LinksListColumn):
    def apply(self, ctx: ColumnContext, record: Dict[str, Any]) -> None:
        value = self.parse(ctx)
        if value is ctx.skip_sentinel:
            return
        if ctx.model_fields is not None and ctx.key not in ctx.model_fields:
            return
        if not value:
            return
        record.setdefault(ctx.key, []).extend(value)


class TyreManufacturersBySeasonScraper(F1TableScraper):
    """
    Scraper producentów opon F1:
    https://en.wikipedia.org/wiki/Formula_One_tyres#Tyre_manufacturers_by_season
    """

    CONFIG = ScraperConfig(
        url="https://en.wikipedia.org/wiki/Formula_One_tyres#Tyre_manufacturers_by_season",
        section_id="Tyre_manufacturers_by_season",
        expected_headers=[
            "Seasons",
            "Manufacturer 1",
            "Wins",
        ],
        column_map={
            "Seasons": "seasons",
            "Manufacturer 1": "manufacturers",
            "Manufacturer 2": "manufacturers",
            "Manufacturer 3": "manufacturers",
            "Manufacturer 4": "manufacturers",
            "Manufacturer 5": "manufacturers",
            "Manufacturer 6": "manufacturers",
            "Wins": "wins",
        },
        columns={
            "seasons": SeasonsColumn(),
            "manufacturers": AppendLinksColumn(),
            "wins": SkipColumn(),
        },
    )


if __name__ == "__main__":
    run_and_export(
        TyreManufacturersBySeasonScraper,
        "tyres/f1_tyre_manufacturers_by_season.json",
        "tyres/f1_tyre_manufacturers_by_season.csv",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
        ),
    )
