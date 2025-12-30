from pathlib import Path
from typing import Any, List

from models.scrape_types.fatality_row import FatalityRow
from scrapers.base.helpers.links import normalize_links
from scrapers.base.helpers.time import parse_date_text
from scrapers.base.helpers.value_objects import NormalizedDate
from scrapers.base.helpers.wiki import strip_marks
from scrapers.base.runner import RunConfig, run_and_export
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.bool import BoolColumn
from scrapers.base.table.columns.types.func import FuncColumn
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.multi import MultiColumn
from scrapers.base.table.columns.types.skip import SkipColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.scraper import F1TableScraper


class F1FatalitiesListScraper(F1TableScraper):
    """
    Lista ofiar śmiertelnych F1 z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_fatalities#Detail_by_driver

    Dodatkowo:
    - is_formula_two_car: znacznik # przy dacie
    - event_is_non_championship: znacznik † w kolumnie Event
    - event_is_test_drive: znacznik ‡ w kolumnie Event
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
            "date": MultiColumn(
                {
                    "date": FuncColumn(
                        lambda ctx: F1FatalitiesListScraper._parse_date(ctx)
                    ),
                    "is_formula_two_car": BoolColumn(
                        lambda ctx: "#" in (ctx.raw_text or "")
                    ),
                }
            ),
            "age": IntColumn(),
            "event": MultiColumn(
                {
                    "event": FuncColumn(
                        lambda ctx: F1FatalitiesListScraper._parse_event(ctx)
                    ),
                    "event_is_non_championship": BoolColumn(
                        lambda ctx: "†" in (ctx.raw_text or "")
                    ),
                    "event_is_test_drive": BoolColumn(
                        lambda ctx: "‡" in (ctx.raw_text or "")
                    ),
                }
            ),
            "circuit": UrlColumn(),
            "car": UrlColumn(),
            "session": TextColumn(),
            "ref": SkipColumn(),
        },
    )

    @staticmethod
    def _parse_date(ctx: ColumnContext) -> NormalizedDate:
        text = (ctx.clean_text or "").replace("#", "").strip()
        if not text:
            return NormalizedDate(text=None, iso=None)
        parsed = parse_date_text(text)
        return NormalizedDate(text=parsed.get("text"), iso=parsed.get("iso"))

    @staticmethod
    def _parse_event(ctx: ColumnContext) -> Any:
        auto_value = AutoColumn().parse(ctx)
        if isinstance(auto_value, dict):
            cleaned = dict(auto_value)
            cleaned["text"] = strip_marks(cleaned.get("text")) or ""
            return cleaned
        if isinstance(auto_value, list):
            return normalize_links(auto_value, strip_marks=True, drop_empty=True)
        if isinstance(auto_value, str):
            return strip_marks(auto_value)
        return auto_value

    def fetch(self) -> List[FatalityRow]:
        rows = super().fetch()
        return rows  # type: ignore[return-value]


if __name__ == "__main__":
    run_and_export(
        F1FatalitiesListScraper,
        "drivers/f1_driver_fatalities.json",
        "drivers/f1_driver_fatalities.csv",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
        ),
    )
