from pathlib import Path
from typing import List

from models.scrape_types.fatality_row import FatalityRow
from scrapers.base.helpers.runner import run_and_export
from scrapers.base.run_config import RunConfig
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.skip import SkipColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.scraper import F1TableScraper
from scrapers.drivers.columns.fatality_date import FatalityDateColumn
from scrapers.drivers.columns.fatality_event import FatalityEventColumn


class F1FatalitiesListScraper(F1TableScraper):
    """
    Lista ofiar śmiertelnych F1 z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_fatalities#Detail_by_driver

    Dodatkowo:
    - formula_category: znacznik # przy dacie (F2) lub domyślnie F1
    - championship: znacznik † w kolumnie Event (False)
    """

    CONFIG = ScraperConfig(
        url="https://en.wikipedia.org/wiki/List_of_Formula_One_fatalities#Detail_by_driver",
        section_id="Detail_by_driver",
        expected_headers=[
            "Driver",
            "Date of accident",
            "Age",
            "Event",
            "Circuit",
            "Car",
            "Session",
        ],
        column_map={
            "Driver": "driver",
            "Date of accident": "date",
            "Age": "age",
            "Event": "event",
            "Circuit": "circuit",
            "Car": "car",
            "Session": "session",
            "Ref.": "ref",
        },
        columns={
            "driver": UrlColumn(),
            "date": FatalityDateColumn(),
            "age": IntColumn(),
            "event": FatalityEventColumn(),
            "circuit": UrlColumn(),
            "car": UrlColumn(),
            "session": TextColumn(),
            "ref": SkipColumn(),
        },
    )

    def fetch(self) -> List[FatalityRow]:
        rows = super().fetch()
        for row in rows:
            formula_category = row.pop("formula_category", None)
            if not formula_category:
                continue
            car = row.get("car")
            if isinstance(car, dict):
                car["formula_category"] = formula_category
            else:
                row["car"] = {
                    "text": car or "",
                    "url": None,
                    "formula_category": formula_category,
                }
        return rows  # type: ignore[return-value]


if __name__ == "__main__":
    run_and_export(
        F1FatalitiesListScraper,
        "drivers/f1_driver_fatalities.json",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
        ),
    )
