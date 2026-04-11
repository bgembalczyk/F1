from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.adapters.factories.dataclass import RECORD_FACTORIES
from scrapers.base.helpers.date_parsing import parse_date_with_category_marker
from scrapers.base.helpers.date_parsing import parse_formula_category
from scrapers.base.helpers.normalize import normalize_auto_value
from scrapers.base.helpers.transformers import append_transformer
from scrapers.base.options import ScraperOptions
from scrapers.base.source_catalog import DRIVERS_FATALITIES
from scrapers.base.table.columns import types as col
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.config import ScraperConfig as TableScraperConfig
from scrapers.base.table.config import build_scraper_config
from scrapers.base.table.dsl.column import ColumnSpec
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.base.table.scraper import F1TableScraper
from scrapers.base.transformers.fatalities_car import FatalitiesCarTransformer
from scrapers.drivers import constants_drivers
from scrapers.drivers.drivers_columns.fatality_date import FatalityDateColumn
from scrapers.drivers.drivers_columns.fatality_event import FatalityEventColumn
from scrapers.drivers.drivers_helpers.parsers import DriverOrderedTableParser
from scrapers.parsers.table.wiki.article import ArticleTablesParser
from scrapers.wiki.parsers.sections.section import SectionParser
from scrapers.wiki.parsers.sections.sub_section import SubSectionParser


class FatalitiesTableParser(DriverOrderedTableParser):
    """Parser wyspecjalizowany dla tabeli „Detail by driver”."""

    table_type = "fatalities_detail_by_driver"
    missing_columns_policy = "require_core_fatalities_columns"
    extra_columns_policy = "ignore"

    _required_headers = frozenset(constants.FATALITIES_HEADERS)
    _column_mapping = {
        constants.FATALITIES_DRIVER_HEADER: "driver",
        constants.FATALITIES_DATE_HEADER: "date",
        constants.FATALITIES_AGE_HEADER: "age",
        constants.FATALITIES_EVENT_HEADER: "event",
        constants.FATALITIES_CIRCUIT_HEADER: "circuit",
        constants.FATALITIES_CAR_HEADER: "car",
        constants.FATALITIES_SESSION_HEADER: "session",
        constants.FATALITIES_REF_HEADER: "ref",
    }

    def matches(self, headers: list[str], _table_data: dict[str, object]) -> bool:
        return self._required_headers.issubset(set(headers))


class DetailByDriverSubSectionParser(SubSectionParser):
    """Parser podsekcji sekcji „Detail by driver” z tabelą ofiar."""

    def __init__(self) -> None:
        super().__init__()
        self._table_parser = ArticleTablesParser(
            specialized_parsers=[FatalitiesTableParser()],
        )

    def parse_group(
        self,
        elements: list,
        *,
        context=None,
    ) -> dict[str, Any]:
        parsed = super().parse_group(elements, context=context)
        tags = [element for element in elements if isinstance(element, Tag)]
        section_fragment = BeautifulSoup("", "html.parser")
        for tag in tags:
            section_fragment.append(tag)
        parsed["tables"] = self._table_parser.parse(section_fragment)
        return parsed


class FatalitiesSectionParser(SectionParser):
    """Parser sekcji H3 dla listy ofiar śmiertelnych F1."""

    def __init__(self) -> None:
        super().__init__()
        self.child_parser = DetailByDriverSubSectionParser()


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
        section_id=constants.FATALITIES_SECTION_ID,
        expected_headers=constants.FATALITIES_HEADERS,
        schema=TableSchemaDSL(
            columns=[
                ColumnSpec(
                    constants.FATALITIES_DRIVER_HEADER,
                    "driver",
                    col.UrlColumn(),
                ),
                ColumnSpec(
                    constants.FATALITIES_DATE_HEADER,
                    "date",
                    FatalityDateColumn(),
                ),
                ColumnSpec(constants.FATALITIES_AGE_HEADER, "age", col.IntColumn()),
                ColumnSpec(
                    constants.FATALITIES_EVENT_HEADER,
                    "event",
                    FatalityEventColumn(),
                ),
                ColumnSpec(
                    constants.FATALITIES_CIRCUIT_HEADER,
                    "circuit",
                    col.UrlColumn(),
                ),
                ColumnSpec(constants.FATALITIES_CAR_HEADER, "car", col.UrlColumn()),
                ColumnSpec(
                    constants.FATALITIES_SESSION_HEADER,
                    "session",
                    col.TextColumn(),
                ),
                ColumnSpec(constants.FATALITIES_REF_HEADER, "ref", col.SkipColumn()),
            ],
        ),
        record_factory=RECORD_FACTORIES.builders("fatality"),
    )

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        config: TableScraperConfig | None = None,
    ) -> None:
        super().__init__(
            options=append_transformer(options, FatalitiesCarTransformer()),
            config=config,
        )
        self.section_parser = FatalitiesSectionParser()

    # Methods using shared utilities from date_parsing module
    # Kept here for backward compatibility if they are used elsewhere
    @staticmethod
    def _parse_date(ctx: ColumnContext) -> str | None:
        return parse_date_with_category_marker(ctx, constants.MARK_F2_CATEGORY)

    @staticmethod
    def _parse_formula_category(ctx: ColumnContext) -> str | None:
        return parse_formula_category(ctx, constants.MARK_F2_CATEGORY)

    @staticmethod
    def _parse_event(ctx: ColumnContext) -> Any:
        championship = constants.MARK_NON_CHAMPIONSHIP_EVENT not in (ctx.raw_text or "")
        auto_value = col.AutoColumn().parse(ctx)
        normalized = normalize_auto_value(auto_value, strip_marks=True)
        return {"event": normalized, "championship": championship}
