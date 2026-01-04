from pathlib import Path
from typing import Any

from scrapers.base.helpers.normalize import normalize_auto_value
from scrapers.base.helpers.runner import run_and_export
from scrapers.base.helpers.time import parse_date_text
from scrapers.base.run_config import RunConfig
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.skip import SkipColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.dsl import TableSchemaDSL, column
from scrapers.base.table.scraper import F1TableScraper
from scrapers.base.transformers import RecordTransformer
from scrapers.base.table.schema import TableSchemaBuilder
from scrapers.base.transformers.fatalities_car import FatalitiesCarTransformer
from scrapers.drivers.columns.fatality_date import FatalityDateColumn
from scrapers.drivers.columns.fatality_event import FatalityEventColumn
from scrapers.drivers.constants import (
    FATALITIES_HEADERS,
    FATALITIES_AGE_HEADER,
    FATALITIES_CAR_HEADER,
    FATALITIES_CIRCUIT_HEADER,
    FATALITIES_DATE_HEADER,
    FATALITIES_DRIVER_HEADER,
    FATALITIES_EVENT_HEADER,
    FATALITIES_REF_HEADER,
    FATALITIES_SESSION_HEADER,
    FATALITIES_SECTION_ID,
    MARK_F2_CATEGORY,
    MARK_NON_CHAMPIONSHIP_EVENT,
)


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
        section_id=FATALITIES_SECTION_ID,
        expected_headers=FATALITIES_HEADERS,
        schema=TableSchemaDSL(
            columns=[
                column(FATALITIES_DRIVER_HEADER, "driver", UrlColumn()),
                column(FATALITIES_DATE_HEADER, "date", FatalityDateColumn()),
                column(FATALITIES_AGE_HEADER, "age", IntColumn()),
                column(FATALITIES_EVENT_HEADER, "event", FatalityEventColumn()),
                column(FATALITIES_CIRCUIT_HEADER, "circuit", UrlColumn()),
                column(FATALITIES_CAR_HEADER, "car", UrlColumn()),
                column(FATALITIES_SESSION_HEADER, "session", TextColumn()),
                column(FATALITIES_REF_HEADER, "ref", SkipColumn()),
            ]
        ),
        record_factory=lambda record: dict(record),
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.transformers = [FatalitiesCarTransformer()]

    @staticmethod
    def _parse_date(ctx: ColumnContext) -> str | None:
        text = (ctx.clean_text or "").replace(MARK_F2_CATEGORY, "").strip()
        if not text:
            return None
        parsed = parse_date_text(text)
        iso = parsed.iso
        if isinstance(iso, list):
            return iso[0] if iso else None
        return iso

    @staticmethod
    def _parse_formula_category(ctx: ColumnContext) -> str | None:
        if not (ctx.raw_text or "").strip():
            return None
        return "F2" if MARK_F2_CATEGORY in (ctx.raw_text or "") else "F1"

    @staticmethod
    def _parse_event(ctx: ColumnContext) -> Any:
        championship = MARK_NON_CHAMPIONSHIP_EVENT not in (ctx.raw_text or "")
        auto_value = AutoColumn().parse(ctx)
        normalized = normalize_auto_value(auto_value, strip_marks=True)
        return {"event": normalized, "championship": championship}

if __name__ == "__main__":
    run_and_export(
        F1FatalitiesListScraper,
        "drivers/f1_driver_fatalities.json",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
            debug_dir=Path("../../data/debug"),
        ),
    )
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.auto import AutoColumn
