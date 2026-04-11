from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.adapters.factories.dataclass import RECORD_FACTORIES
from scrapers.columns.context import ColumnContext
from scrapers.columns.factory import IntColumn
from scrapers.columns.spec import ColumnSpec
from scrapers.columns.types.auto import AutoColumn
from scrapers.columns.types.fatality_date import FatalityDateColumn
from scrapers.columns.types.fatality_event import FatalityEventColumn
from scrapers.columns.types.skip import SkipColumn
from scrapers.columns.types.text import TextColumn
from scrapers.columns.types.url import UrlColumn
from scrapers.config_table import TableScraperConfig
from scrapers.config_table import build_scraper_config
from scrapers.constants_drivers import FATALITIES_AGE_HEADER
from scrapers.constants_drivers import FATALITIES_CAR_HEADER
from scrapers.constants_drivers import FATALITIES_CIRCUIT_HEADER
from scrapers.constants_drivers import FATALITIES_DATE_HEADER
from scrapers.constants_drivers import FATALITIES_DRIVER_HEADER
from scrapers.constants_drivers import FATALITIES_EVENT_HEADER
from scrapers.constants_drivers import FATALITIES_HEADERS
from scrapers.constants_drivers import FATALITIES_REF_HEADER
from scrapers.constants_drivers import FATALITIES_SECTION_ID
from scrapers.constants_drivers import FATALITIES_SESSION_HEADER
from scrapers.constants_drivers import MARK_F2_CATEGORY
from scrapers.constants_drivers import MARK_NON_CHAMPIONSHIP_EVENT
from scrapers.driver_ordered_table_parser import DriverOrderedTableParser
from scrapers.helpers.date_parsing import parse_date_with_category_marker
from scrapers.helpers.date_parsing import parse_formula_category
from scrapers.helpers.normalize import normalize_auto_value
from scrapers.helpers.transformers import append_transformer
from scrapers.options import ScraperOptions
from scrapers.parsers.section.protocol import SectionParser
from scrapers.parsers.section.sublevels import SubSectionParser
from scrapers.parsers.table.wiki.article import ArticleTablesParser
from scrapers.scraper_table import F1TableScraper
from scrapers.source_catalog import DRIVERS_FATALITIES
from scrapers.table_schema_dsl import TableSchemaDSL
from scrapers.transformers.record.fatalities_car import FatalitiesCarTransformer


class FatalitiesTableParser(DriverOrderedTableParser):
    """Parser wyspecjalizowany dla tabeli „Detail by driver”."""

    table_type = "fatalities_detail_by_driver"
    missing_columns_policy = "require_core_fatalities_columns"
    extra_columns_policy = "ignore"

    _required_headers = frozenset(FATALITIES_HEADERS)
    _column_mapping = {
        FATALITIES_DRIVER_HEADER: "driver",
        FATALITIES_DATE_HEADER: "date",
        FATALITIES_AGE_HEADER: "age",
        FATALITIES_EVENT_HEADER: "event",
        FATALITIES_CIRCUIT_HEADER: "circuit",
        FATALITIES_CAR_HEADER: "car",
        FATALITIES_SESSION_HEADER: "session",
        FATALITIES_REF_HEADER: "ref",
    }

    def matches(self, headers: list[str], _table_data: dict[str, object]) -> bool:
        return self._required_headers.issubset(set(headers))


class DetailByDriverSubSectionParser(SubSectionParser):
    """Parser podsekcji sekcji „Detail by driver” z tabelą ofiar."""

    def __init__(self) -> None:
        super().__init__()
        self._table_parser = ArticleTablesParser(
            specialized_mappers=[FatalitiesTableParser()],
        )

    def _parse_group(
        self,
        elements: list,
        *,
        context=None,
    ) -> dict[str, Any]:
        parsed = super()._parse_group(elements, context=context)
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
        section_id=FATALITIES_SECTION_ID,
        expected_headers=FATALITIES_HEADERS,
        schema=TableSchemaDSL(
            columns=[
                ColumnSpec(
                    FATALITIES_DRIVER_HEADER,
                    "driver",
                    UrlColumn(),
                ),
                ColumnSpec(
                    FATALITIES_DATE_HEADER,
                    "date",
                    FatalityDateColumn(),
                ),
                ColumnSpec(FATALITIES_AGE_HEADER, "age", IntColumn()),
                ColumnSpec(
                    FATALITIES_EVENT_HEADER,
                    "event",
                    FatalityEventColumn(),
                ),
                ColumnSpec(
                    FATALITIES_CIRCUIT_HEADER,
                    "circuit",
                    UrlColumn(),
                ),
                ColumnSpec(FATALITIES_CAR_HEADER, "car", UrlColumn()),
                ColumnSpec(
                    FATALITIES_SESSION_HEADER,
                    "session",
                    TextColumn(),
                ),
                ColumnSpec(FATALITIES_REF_HEADER, "ref", SkipColumn()),
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
