from typing import Any

from scrapers.base.factory.record_factory import RECORD_FACTORIES
from scrapers.base.options import ScraperOptions
from scrapers.base.source_catalog import FEMALE_DRIVERS_LIST
from scrapers.base.table.columns.types import LinksListColumn
from scrapers.base.table.columns.types import SeasonsColumn
from scrapers.base.table.columns.types import SkipColumn
from scrapers.base.table.columns.types import UrlColumn
from scrapers.base.table.columns.types.points import PointsColumn
from scrapers.base.table.config import build_scraper_config
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.base.table.scraper import F1TableScraper
from scrapers.drivers.columns.entries_starts import EntriesStartsColumn
from scrapers.drivers.constants import FEMALE_DRIVER_ENTRIES_STARTS_HEADER
from scrapers.drivers.constants import FEMALE_DRIVER_NAME_HEADER
from scrapers.drivers.constants import FEMALE_DRIVER_POINTS_HEADER
from scrapers.drivers.constants import FEMALE_DRIVER_SEASONS_HEADER
from scrapers.drivers.constants import FEMALE_DRIVER_TEAMS_HEADER
from scrapers.drivers.constants import FEMALE_DRIVERS_HEADERS
from scrapers.drivers.constants import FEMALE_DRIVERS_INDEX_HEADER
from scrapers.drivers.constants import FEMALE_DRIVERS_SECTION_ID
from scrapers.wiki.parsers.elements.wiki_table.base import WikiTableBaseParser
from scrapers.wiki.parsers.sections.section import SectionParser
from scrapers.wiki.parsers.sections.sub_section import SubSectionParser


class FemaleDriversTableParser(WikiTableBaseParser):
    table_type = "female_drivers_list"
    missing_columns_policy = "ignore"
    extra_columns_policy = "ignore"

    _column_mapping = {
        FEMALE_DRIVER_NAME_HEADER: "driver",
        FEMALE_DRIVER_SEASONS_HEADER: "seasons",
        FEMALE_DRIVER_TEAMS_HEADER: "teams",
        FEMALE_DRIVER_ENTRIES_STARTS_HEADER: "entries_starts",
        FEMALE_DRIVER_POINTS_HEADER: "points",
    }

    def matches(self, headers: list[str], _table_data: dict[str, Any]) -> bool:
        required_headers = set(FEMALE_DRIVERS_HEADERS)
        return required_headers.issubset(set(headers))

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        return {
            header: self._column_mapping[header]
            for header in headers
            if header in self._column_mapping
        }

    @staticmethod
    def build_schema() -> TableSchemaDSL:
        return TableSchemaDSL(
            columns=[
                column(FEMALE_DRIVERS_INDEX_HEADER, "_skip", SkipColumn()),
                column(FEMALE_DRIVER_NAME_HEADER, "driver", UrlColumn()),
                column(FEMALE_DRIVER_SEASONS_HEADER, "seasons", SeasonsColumn()),
                column(FEMALE_DRIVER_TEAMS_HEADER, "teams", LinksListColumn()),
                column(
                    FEMALE_DRIVER_ENTRIES_STARTS_HEADER,
                    "entries_starts",
                    EntriesStartsColumn(),
                ),
                column(FEMALE_DRIVER_POINTS_HEADER, "points", PointsColumn()),
            ],
        )


class OfficialDriversSubSectionParser(SubSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self._table_parser = FemaleDriversTableParser()

    def parse_group(
        self,
        elements: list,
        *,
        context=None,
    ) -> dict[str, Any]:
        parsed = super().parse_group(elements, context=context)
        self._apply_female_drivers_table_parser(parsed)
        return parsed

    def _apply_female_drivers_table_parser(self, payload: dict[str, Any]) -> None:
        for section in payload.get("sub_sub_sections", []):
            self._apply_for_elements(section.get("elements", []))
            self._apply_female_drivers_table_parser(section)

    def _apply_for_elements(self, elements: list[dict[str, Any]]) -> None:
        for element in elements:
            if element.get("kind") != "table":
                continue
            data = element.get("data")
            if not isinstance(data, dict):
                continue
            parsed = self._table_parser.parse(data)
            if parsed is not None:
                element["data"] = parsed


class DriversSectionParser(SectionParser):
    def __init__(self) -> None:
        super().__init__()
        self.child_parser = OfficialDriversSubSectionParser()


class FemaleDriversListScraper(F1TableScraper):
    """
    Scraper listy oficjalnych kobiet-kierowców F1 z:
    https://en.wikipedia.org/wiki/List_of_female_Formula_One_drivers
    """

    CONFIG = build_scraper_config(
        url=FEMALE_DRIVERS_LIST.base_url,
        section_id=FEMALE_DRIVERS_SECTION_ID,
        expected_headers=FEMALE_DRIVERS_HEADERS,
        schema=FemaleDriversTableParser.build_schema(),
        record_factory=RECORD_FACTORIES.builders("special_driver"),
    )

    def __init__(self, *, options: ScraperOptions | None = None) -> None:
        super().__init__(options=options)
        parser = DriversSectionParser()
        self.section_parser = parser
        self.body_content_parser.content_text_parser.section_parser = parser
