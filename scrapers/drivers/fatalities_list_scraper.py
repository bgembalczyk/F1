from typing import Any

from models.records.factories.build import RECORD_BUILDERS
from scrapers.base.source_catalog import DRIVERS_FATALITIES
from scrapers.base.helpers.date_parsing import parse_date_with_category_marker
from scrapers.base.helpers.date_parsing import parse_formula_category
from scrapers.base.helpers.normalize import normalize_auto_value
from scrapers.base.options import ScraperOptions
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types import AutoColumn
from scrapers.base.table.columns.types import IntColumn
from scrapers.base.table.columns.types import SkipColumn
from scrapers.base.table.columns.types import TextColumn
from scrapers.base.table.columns.types import UrlColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.config import build_scraper_config
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.base.table.scraper import F1TableScraper
from scrapers.base.transformers.fatalities_car import FatalitiesCarTransformer
from scrapers.drivers.columns.fatality_date import FatalityDateColumn
from scrapers.drivers.columns.fatality_event import FatalityEventColumn
from scrapers.drivers.constants import FATALITIES_AGE_HEADER
from scrapers.drivers.constants import FATALITIES_CAR_HEADER
from scrapers.drivers.constants import FATALITIES_CIRCUIT_HEADER
from scrapers.drivers.constants import FATALITIES_DATE_HEADER
from scrapers.drivers.constants import FATALITIES_DRIVER_HEADER
from scrapers.drivers.constants import FATALITIES_EVENT_HEADER
from scrapers.drivers.constants import FATALITIES_HEADERS
from scrapers.drivers.constants import FATALITIES_REF_HEADER
from scrapers.drivers.constants import FATALITIES_SECTION_ID
from scrapers.drivers.constants import FATALITIES_SESSION_HEADER
from scrapers.drivers.constants import MARK_F2_CATEGORY
from scrapers.drivers.constants import MARK_NON_CHAMPIONSHIP_EVENT


class F1FatalitiesListScraper(F1TableScraper):
    """
    Lista ofiar śmiertelnych F1 z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_fatalities#Detail_by_driver

    Dodatkowo:
    - formula_category: znacznik # przy dacie (F2) lub domyślnie F1
    - championship: znacznik † w kolumnie Event (False)
    """

    CONFIG = build_scraper_config(
        url=DRIVERS_FATALITIES.url(),
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
            ],
        ),
        record_factory=RECORD_BUILDERS.fatality,
    )

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        config: ScraperConfig | None = None,
    ) -> None:
        options = options or ScraperOptions()
        options.transformers = [
            *list(options.transformers or []),
            FatalitiesCarTransformer(),
        ]
        super().__init__(options=options, config=config)

    # Methods using shared utilities from date_parsing module
    # Kept here for backward compatibility if they are used elsewhere
    @staticmethod
    def _parse_date(ctx: ColumnContext) -> str | None:
        return parse_date_with_category_marker(ctx, MARK_F2_CATEGORY)

    @staticmethod
    def _parse_formula_category(ctx: ColumnContext) -> str | None:
        return parse_formula_category(ctx, MARK_F2_CATEGORY)

    @staticmethod
    def _parse_event(ctx: ColumnContext) -> Any:
        championship = MARK_NON_CHAMPIONSHIP_EVENT not in (ctx.raw_text or "")
        auto_value = AutoColumn().parse(ctx)
        normalized = normalize_auto_value(auto_value, strip_marks=True)
        return {"event": normalized, "championship": championship}


if __name__ == "__main__":
    from scrapers.base.deprecated_entrypoint import run_deprecated_entrypoint

    run_deprecated_entrypoint()
