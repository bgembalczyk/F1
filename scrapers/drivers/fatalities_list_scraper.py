from pathlib import Path
from typing import Any, List

from scrapers.base.helpers.links import normalize_links
from scrapers.base.helpers.runner import run_and_export
from scrapers.base.helpers.time import parse_date_text
from scrapers.base.helpers.wiki import strip_marks
from scrapers.base.records import ExportRecord
from scrapers.base.run_config import RunConfig
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.skip import SkipColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.scraper import F1TableScraper
from scrapers.base.table.schema import TableSchemaBuilder
from scrapers.drivers.columns.fatality_date import FatalityDateColumn
from scrapers.drivers.columns.fatality_event import FatalityEventColumn
from scrapers.drivers.constants import (
    FATALITIES_HEADERS,
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
        schema=(
            TableSchemaBuilder()
            .map("Driver", "driver", UrlColumn())
            .map("Date of accident", "date", FatalityDateColumn())
            .map("Age", "age", IntColumn())
            .map("Event", "event", FatalityEventColumn())
            .map("Circuit", "circuit", UrlColumn())
            .map("Car", "car", UrlColumn())
            .map("Session", "session", TextColumn())
            .map("Ref.", "ref", SkipColumn())
        ),
    )

    @staticmethod
    def _parse_date(ctx: ColumnContext) -> str | None:
        text = (ctx.clean_text or "").replace(MARK_F2_CATEGORY, "").strip()
        if not text:
            return None
        parsed = parse_date_text(text)
        return parsed.get("iso")

    @staticmethod
    def _parse_formula_category(ctx: ColumnContext) -> str | None:
        if not (ctx.raw_text or "").strip():
            return None
        return "F2" if MARK_F2_CATEGORY in (ctx.raw_text or "") else "F1"

    @staticmethod
    def _parse_event(ctx: ColumnContext) -> Any:
        championship = MARK_NON_CHAMPIONSHIP_EVENT not in (ctx.raw_text or "")
        auto_value = AutoColumn().parse(ctx)
        if isinstance(auto_value, dict):
            cleaned = dict(auto_value)
            cleaned["text"] = strip_marks(cleaned.get("text")) or ""
            return {"event": cleaned, "championship": championship}
        if isinstance(auto_value, list):
            return {
                "event": normalize_links(auto_value, strip_marks=True, drop_empty=True),
                "championship": championship,
            }
        if isinstance(auto_value, str):
            return {"event": strip_marks(auto_value), "championship": championship}
        return {"event": auto_value, "championship": championship}

    def post_process_records(self, records: List[ExportRecord]) -> List[ExportRecord]:
        before_count = len(records)
        self.logger.debug("Post-processing fatality records: %d", before_count)

        for row in records:
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

        self.logger.debug(
            "Post-processing fatality records complete: %d -> %d",
            before_count,
            len(records),
        )
        return records  # type: ignore[return-value]


if __name__ == "__main__":
    run_and_export(
        F1FatalitiesListScraper,
        "drivers/f1_driver_fatalities.json",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
        ),
    )
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.auto import AutoColumn
